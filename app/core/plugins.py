import asyncio
import contextlib
import importlib
import json
import shutil
import sys
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Union

from graia.scheduler import GraiaScheduler
from loguru import logger
from pip import main as pip
from prettytable import PrettyTable
from retrying import retry

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.core.database import db_init, db_update
from app.core.exceptions import LocalPluginNotFoundError, NonStandardPluginError
from app.util.decorator import Singleton
from app.util.network import download, general_request
from app.util.text2image import create_image
from app.util.tools import app_path, to_thread
from app.util.version import compare_version


class PluginType(Enum):
    """描述插件类型"""

    Basic = "basic"
    """基础插件"""
    Extension = "extension"
    """扩展插件"""

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        type_map: Dict[str, str] = {"basic": "<基础插件>", "extension": "<扩展插件>"}
        return type_map[self.value]


class PluginManager(metaclass=Singleton):
    """
    Madoka 插件管理器
    """

    __plugins: Dict[str, ModuleType]
    __ignore = ["__init__.py", "__pycache__"]
    __base_path = app_path().joinpath("plugin")
    __base_url = f"https://raw.fastgit.org/MadokaProject/Plugins/{Config().REMOTE_REPO_VERSION}/"
    __folder_path = __base_path.joinpath("extension")
    __info_path = __base_path.joinpath("plugin.json")

    def __init__(self):
        self.__plugins = {}
        self.__manager: CommandDelegateManager = CommandDelegateManager()
        self.__app: AppCore = AppCore()
        self.__sche: GraiaScheduler = self.__app.get_scheduler()

    def get_plugins(self):
        return self.__plugins

    async def load(
        self,
        plugin_info: Union[str, Dict[str, str]],
        plugin_type: PluginType = PluginType.Extension,
    ) -> bool:
        """加载插件

        :param plugin_info: 插件名称或插件信息字典
        :param plugin_type: 插件类型
        """
        plugins = ()
        if isinstance(plugin_info, str):
            plugins = (f"app.plugin.{plugin_type}.{plugin_info}",)
            plugin_info = plugins[0]
        elif isinstance(plugin_info, dict):
            plugins = (
                f"app.plugin.{plugin_type.value}.{plugin_info['root_dir']}.{plugin.name.split('.')[0]}"
                for plugin in self.__base_path.joinpath(plugin_type.value, plugin_info["root_dir"]).glob(pattern="*.py")
                if plugin.name not in self.__ignore and plugin.is_file()
            )
            plugin_info = f"app.plugin.{plugin_type}.{plugin_info['root_dir']}"
        try:
            for plugin in plugins:
                if not await self.is_load(plugin):
                    self.__plugins[plugin] = importlib.import_module(plugin)
                else:
                    logger.warning(f"该插件已加载!{plugin}")
                    return True
            logger.success(f"成功加载插件: {plugin_info}")
            return True
        except ImportError as e:
            logger.error(f"插件加载失败: {plugin_info} - {e}")
            return False
        except RuntimeError as e:
            # TODO: return 出去后尝试卸载插件
            logger.error(f"插件加载失败: {e}")
            raise NonStandardPluginError(plugin_info) from e
        except Exception as e:
            logger.exception(e)
            return False

    async def loads(self, plugins: Dict[str, PluginType]) -> Dict[str, bool]:
        """批量加载插件

        :param plugins: 插件名称与插件类型的字典
        """
        return {plugin_name: await self.load(plugin_name, plugin_type) for plugin_name, plugin_type in plugins.items()}

    async def loads_basic(self) -> None:
        """加载基础插件"""
        plugins: Dict[str, PluginType] = {
            f"{plugin.parent.name}.{plugin.name.split('.')[0]}": PluginType.Basic
            for plugin in sorted(self.__base_path.joinpath("basic").glob(pattern="*/*.py"))
            if plugin.name not in self.__ignore and plugin.is_file()
        }
        await self.loads(plugins)

    async def loads_extension(self) -> None:
        """加载扩展插件"""
        self.__folder_path.mkdir(exist_ok=True)
        plugins: Dict[str, PluginType] = {
            f"{plugin.parent.name}.{plugin.name.split('.')[0]}": PluginType.Extension
            for plugin in sorted(self.__folder_path.glob(pattern="*/*.py"))
            if plugin.name not in self.__ignore and plugin.is_file()
        }
        await self.loads(plugins)

    async def loads_all(self) -> None:
        """加载所有插件
        仅允许初始化时使用
        """
        self.__plugins.clear()
        await self.loads_basic()
        await self.loads_extension()
        db_init()
        db_update()

    def reload(
        self,
        plugin_info: Union[str, Dict[str, str]] = "all_plugin",
        plugin_type: PluginType = PluginType.Extension,
    ) -> bool:
        """重载插件

        :param plugin_info: 插件名称或插件信息字典
        :param plugin_type: 指定插件类型
        """
        if plugin_info == "all_plugin":
            for module in self.__plugins.values():
                self._extracted_from_reload(module)
                logger.success(f"重载插件: {module.__name__} 成功")
            return True
        plugins = (
            f"app.plugin.{plugin_type.value}.{plugin_info}.{plugin.name.split('.')[0]}"
            for plugin in self.__folder_path.joinpath(plugin_info).glob(pattern="*.py")
            if plugin.name not in self.__ignore and plugin.is_file()
        )
        for plugin in plugins:
            if module := self.__plugins.get(plugin):
                self._extracted_from_reload(module)
                logger.success(f"重载插件: {plugin} 成功")
            else:
                logger.warning(f"插件: {plugin} 未加载")
                return False
        return True

    def _extracted_from_reload(self, module):
        self.__manager.delete(module)
        self.remove_tasker(module)
        importlib.reload(module)

    def unload(self, root_dir: str) -> bool:
        """卸载插件
        仅支持卸载扩展插件

        :param root_dir: 插件所在目录
        """
        plugins = (
            f"{plugin.parent.name}.{plugin.name.split('.')[0]}"
            for plugin in self.__folder_path.joinpath(root_dir).glob(pattern="*.py")
            if plugin.name not in self.__ignore and plugin.is_file()
        )
        if not plugins:
            logger.warning("卸载失败，无此插件！")
            raise LocalPluginNotFoundError(root_dir)
        for plugin in plugins:
            plugin_name = f"app.plugin.extension.{plugin}"
            if plugin_name in sys.modules.keys():
                sys.modules.pop(plugin_name)
                __plugin = self.__plugins.get(plugin_name)
                self.remove_tasker(__plugin)
                self.__manager.delete(__plugin)
                self.__plugins.pop(plugin_name)
                logger.success(f"卸载扩展插件成功: {plugin_name}")
            else:
                logger.warning("该扩展插件未加载")
                return False
        return True

    def remove_tasker(self, tasks: ModuleType):
        """移除计划任务"""
        for tasker in self.__sche.schedule_tasks.copy():
            if tasks.__name__ == tasker.target.__module__:
                tasker.stop()
                self.__sche.schedule_tasks.remove(tasker)

    async def is_load(self, plugin: Union[str, ModuleType]) -> bool:
        """查找插件是否加载"""
        if isinstance(plugin, ModuleType):
            plugin = plugin.__name__
        return bool(self.__plugins.get(plugin))

    async def exist(self, plugin_info: Dict[str, str]) -> bool:
        """查找插件是否存在

        :param plugin_info: 插件信息字典
        """
        return bool(await self.get_info(plugin_info))

    async def get_info(self, plugins: Union[str, Dict[str, str]]) -> List[Dict[str, str]]:
        """获取插件信息

        :param plugins: 插件名称或插件信息字典
        """
        try:
            with open(self.__info_path, "r", encoding="UTF-8") as f:
                plugin_infos = json.load(f)
            if isinstance(plugins, str):
                if plugins == "*":
                    return plugin_infos
                return [plugin for plugin in plugin_infos if plugin["name"] == plugins]
            elif isinstance(plugins, dict):
                for plugin in plugin_infos:
                    if plugin["name"] == plugins["name"] and plugin["author"] == plugins["author"]:
                        return [plugin]
        except FileNotFoundError:
            return []

    async def record_info(self, plugin_info: Dict[str, str]) -> None:
        """记录插件信息

        :param plugin_info: 插件信息
        """
        plugin_infos: List[Dict] = []
        with contextlib.suppress(FileNotFoundError):
            with open(self.__info_path, "r", encoding="UTF-8") as f:
                plugin_infos = json.load(f)
            if local_plugin_info := await self.get_info(plugin_info):
                plugin_infos.remove(local_plugin_info[0])
        plugin_infos.append(plugin_info)
        with open(self.__info_path, "w", encoding="UTF-8") as f:
            json.dump(plugin_infos, f, indent=4, ensure_ascii=False)

    async def remove_info(self, plugin_info: Dict[str, str]) -> None:
        """删除插件信息

        :param plugin_info: 插件信息
        """
        plugin_infos: List[Dict] = []
        with contextlib.suppress(FileNotFoundError):
            with open(self.__info_path, "r", encoding="UTF-8") as f:
                plugin_infos = json.load(f)
            if local_plugin_info := await self.get_info(plugin_info):
                plugin_infos.remove(local_plugin_info[0])
        with open(self.__info_path, "w", encoding="UTF-8") as f:
            json.dump(plugin_infos, f, indent=4, ensure_ascii=False)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    async def get_remote_info(self, info: str = "list.json") -> List:
        """获取远程插件信息

        :param info: 插件信息文件名
        """
        await asyncio.sleep(1)
        return json.loads(await general_request(self.__base_url + info, method="get"))

    async def download(self, root_dir: str, url_lists: List[str]) -> bool:
        """通过远程插件地址获取插件

        :param root_dir: 插件所在目录
        :param url_lists: 插件资源列表
        """
        for url in url_lists:
            Path(f"{self.__folder_path}/{root_dir}{''.join(f'/{i}' for i in url.split('/')[:-1])}").mkdir(
                parents=True, exist_ok=True
            )
            filepath = self.__folder_path.joinpath(f"{root_dir}/{url}")
            await asyncio.sleep(1)
            if not await to_thread(download, f"{self.__base_url}{root_dir}/{url}", filepath):
                return False
        return True

    async def install(self, plugin_info: Dict[str, str]) -> bool:
        """安装插件

        :param plugin_info: 插件信息
        """
        logger.info(f"正在尝试安装插件: {plugin_info['name']} - {plugin_info['author']}")
        resource_urls: list = await self.get_remote_info(f'{plugin_info["root_dir"]}/resource.json')
        if plugin_info["pypi"]:
            resource_urls.append("requirements.txt")
        if await self.download(plugin_info["root_dir"], resource_urls):
            if plugin_info["pypi"]:
                await to_thread(
                    pip,
                    [
                        "install",
                        "-r",
                        str(self.__folder_path.joinpath(f"{plugin_info['root_dir']}/requirements.txt")),
                        "-i",
                        "https://pypi.tuna.tsinghua.edu.cn/simple",
                    ],
                )
            plugin_path = self.__folder_path.joinpath(plugin_info["root_dir"])
            plugins = {
                f"{plugin.parent.name}.{plugin.name.split('.')[0]}": PluginType.Extension
                for plugin in plugin_path.glob(pattern="*.py")
                if plugin.name not in self.__ignore and plugin.is_file()
            }
            try:
                await self.loads(plugins)
                db_init(plugin_path)
                db_update(plugin_path)
            except Exception as e:
                logger.exception(e)
                self.__app.stop()
            await self.record_info(plugin_info)
            logger.success(f"插件安装成功: {plugin_info['name']} - {plugin_info['author']}")
            return True
        else:
            logger.error(f"插件安装失败，请尝试重新安装: {plugin_info['name']} - {plugin_info['author']}")
            return False

    def delete(self, plugin_info: Dict[str, str]) -> None:
        """删除插件

        仅支持删除扩展插件

        :param plugin_info: 插件信息
        """
        self.unload(plugin_info["root_dir"])
        shutil.rmtree(self.__folder_path.joinpath(plugin_info["root_dir"]))
        asyncio.create_task(self.remove_info(plugin_info))
        logger.success(f"插件删除成功: {plugin_info['name']} - {plugin_info['author']}")

    async def check_update(self) -> Union[None, bytes]:
        """检查更新"""
        local_plugins = await self.get_info("*")
        if not local_plugins:
            return
        remote_plugins = await self.get_remote_info()
        is_update = False
        msg = PrettyTable()
        msg.field_names = ["插件名", "作者", "当前版本", "最新版本"]
        for local_plugin in local_plugins:
            for remote_plugin in remote_plugins:
                if (
                    local_plugin["name"] == remote_plugin["name"]
                    and local_plugin["author"] == remote_plugin["author"]
                    and compare_version(remote_plugin["version"], local_plugin["version"])
                ):
                    is_update = True
                    msg.add_row(
                        [
                            local_plugin["name"],
                            local_plugin["author"],
                            local_plugin["version"],
                            remote_plugin["version"],
                        ]
                    )
                    break
        if is_update:
            return await create_image(msg.get_string(), cut=150)
