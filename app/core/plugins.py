import asyncio
import importlib
import json
import shutil
import sys
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Dict, Union, List

from graia.scheduler import GraiaScheduler
from loguru import logger
from pip import main as pip
from prettytable import PrettyTable
from retrying import retry

from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.util.network import general_request, download
from app.util.tools import app_path, to_thread
from .exceptions import *
from ..util.text2image import create_image
from ..util.version import compare_version


class PluginType(Enum):
    """描述插件类型"""
    Basic = "basic"
    """基础插件"""
    Extension = "extension"
    """扩展插件"""

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        type_map: Dict[str, str] = {
            "basic": "<基础插件>",
            "extension": "<扩展插件>"
        }
        return type_map[self.value]


class PluginManager:
    """
    Madoka 插件管理器
    """
    __instance = None
    __first_init: bool = False
    __plugins: Dict[str, ModuleType]
    __ignore = ["__init__.py", "__pycache__"]
    __base_path = app_path().joinpath('plugin')
    __base_url = f"https://madokaproject.coding.net/p/p/d/plugins/git/raw/{Config.REMOTE_REPO_VERSION}/"
    __folder_path = __base_path.joinpath('extension')
    __info_path = __base_path.joinpath('plugin.json')

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__first_init:
            self.__plugins = {}
            self.__first_init = True
            self.__manager: CommandDelegateManager = CommandDelegateManager.get_instance()
            from app.core.app import AppCore
            self.__sche: GraiaScheduler = AppCore.get_core_instance().get_scheduler()
        else:
            raise PluginManagerAlreadyInitialized

    @classmethod
    def get_instance(cls):
        """获取插件管理器实例"""
        if cls.__instance:
            return cls.__instance
        else:
            raise PluginManagerInitialized

    def get_plugins(self):
        return self.__plugins

    async def load_plugin(
            self,
            plugin_info: Union[str, Dict[str, str]],
            plugin_type: PluginType = PluginType.Extension
    ) -> bool:
        """加载插件

        :param plugin_info: 插件名称或插件信息字典
        :param plugin_type: 插件类型
        """
        plugins = []
        if isinstance(plugin_info, str):
            plugins = [f"app.plugin.{plugin_type}.{plugin_info}"]
            plugin_info = plugins[0]
        elif isinstance(plugin_info, dict):
            for plugin in self.__base_path.joinpath(plugin_type.value, plugin_info['root_dir']).rglob(pattern='*.py'):
                if plugin.name not in self.__ignore and plugin.is_file():
                    plugins.append(f"app.plugin.{plugin_type.value}.{plugin_info['root_dir']}.{plugin.name.split('.')[0]}")
            plugin_info = f"app.plugin.{plugin_type}.{plugin_info['root_dir']}"
        try:
            for plugin in plugins:
                if not await self.find_plugin(plugin):
                    self.__plugins[plugin] = importlib.import_module(plugin)
                else:
                    logger.warning('该插件已加载!' + plugin)
                    return True
            logger.success("成功加载插件: " + plugin_info)
            return True
        except ModuleNotFoundError as e:
            logger.error(f"插件加载失败: {plugin_info} - {e}")
            return False
        except ImportError as e:
            logger.error(f"插件加载失败: {plugin_info} - {e}")
            return False

    async def loads_plugin(self, plugins: Dict[str, PluginType]) -> Dict[str, bool]:
        """批量加载插件

        :param plugins: 插件名称与插件类型的字典
        """
        result = {}
        for plugin_name, plugin_type in plugins.items():
            result.update({plugin_name: await self.load_plugin(plugin_name, plugin_type)})
        return result

    async def loads_basic_plugin(self) -> None:
        """加载基础插件"""
        plugins = {}
        for plugin in sorted(self.__base_path.joinpath('basic').rglob(pattern='*.py')):
            if plugin.name not in self.__ignore and plugin.is_file():
                plugin_name = f"{plugin.parent.name}.{plugin.name.split('.')[0]}"
                plugins.update({plugin_name: PluginType.Basic})
        await self.loads_plugin({plugin: PluginType.Basic for plugin in plugins})

    async def loads_extension_plugin(self) -> None:
        """加载扩展插件"""
        plugins = {}
        self.__folder_path.mkdir(exist_ok=True)
        for plugin in sorted(self.__folder_path.rglob(pattern='*.py')):
            if plugin.name not in self.__ignore and plugin.is_file():
                plugin_name = f"{plugin.parent.name}.{plugin.name.split('.')[0]}"
                plugins.update({plugin_name: PluginType.Extension})
        await self.loads_plugin(plugins)

    async def loads_all_plugin(self) -> None:
        """加载所有插件
        仅允许初始化时使用
        """
        self.__plugins.clear()
        await self.loads_basic_plugin()
        await self.loads_extension_plugin()

    def reload_plugin(
            self,
            plugin_info: Union[str, Dict[str, str]] = 'all_plugin',
            plugin_type: PluginType = PluginType.Extension
    ) -> bool:
        """重载插件

        :param plugin_info: 插件名称或插件信息字典
        :param plugin_type: 指定插件类型
        """
        if plugin_info == 'all_plugin':
            for module in self.__plugins.values():
                self.__manager.delete(module)
                self.remove_tasker(module)
                importlib.reload(module)
                logger.success(f"重载插件: {module.__name__} 成功")
            return True
        plugins = []
        for plugin in self.__folder_path.joinpath(plugin_info).rglob(pattern='*.py'):
            if plugin.name not in self.__ignore and plugin.is_file():
                plugins.append(f"app.plugin.{plugin_type.value}.{plugin_info}.{plugin.name.split('.')[0]}")
        for plugin in plugins:
            if module := self.__plugins.get(plugin):
                self.__manager.delete(module)
                self.remove_tasker(module)
                importlib.reload(module)
                logger.success(f"重载插件: {plugin} 成功")
            else:
                logger.warning(f"插件: {plugin} 未加载")
                return False
        return True

    def unload_plugin(self, root_dir: str) -> bool:
        """卸载插件
        仅支持卸载扩展插件

        :param root_dir: 插件所在目录
        """
        plugins = []
        for plugin in self.__folder_path.joinpath(root_dir).rglob(pattern='*.py'):
            if plugin.name not in self.__ignore and plugin.is_file():
                plugin_name = f"{plugin.parent.name}.{plugin.name.split('.')[0]}"
                plugins.append(plugin_name)

        if not plugins:
            logger.warning('卸载失败，无此插件！')
            raise LocalPluginNotFound
        for plugin in plugins:
            plugin_name = f"app.plugin.extension.{plugin}"
            if plugin_name in sys.modules.keys():
                sys.modules.pop(plugin_name)
                __plugin = self.__plugins.get(plugin_name)
                self.remove_tasker(__plugin)
                self.__manager.delete(__plugin)
                self.__plugins.pop(plugin_name)
                logger.success('卸载扩展插件成功: ' + plugin_name)
            else:
                logger.warning('该扩展插件未加载')
                return False
        return True

    def remove_tasker(self, tasks: ModuleType):
        """移除计划任务"""
        for tasker in self.__sche.schedule_tasks.copy():
            if tasks.__name__ == tasker.target.__module__:
                tasker.stop()
                self.__sche.schedule_tasks.remove(tasker)

    async def find_plugin(self, plugin: Union[str, ModuleType]) -> bool:
        """查找插件是否加载"""
        if isinstance(plugin, ModuleType):
            plugin = plugin.__name__
        if self.__plugins.get(plugin):
            return True
        return False

    async def find_plugin_exist(self, plugin_info: Dict[str, str]) -> bool:
        """查找插件是否存在

        :param plugin_info: 插件信息字典
        """
        if await self.get_plugin_info(plugin_info):
            return True
        return False

    async def get_plugin_info(self, plugins: Union[str, Dict[str, str]]) -> List[Dict[str, str]]:
        """获取插件信息

        :param plugins: 插件名称或插件信息字典
        """
        with open(self.__info_path, 'r') as f:
            plugin_infos = json.load(f)
        if isinstance(plugins, str):
            if plugins == '*':
                return plugin_infos
            return [plugin for plugin in plugin_infos if plugin['name'] == plugins]
        elif isinstance(plugins, dict):
            for plugin in plugin_infos:
                if plugin['name'] == plugins['name'] and plugin['author'] == plugins['author']:
                    return [plugin]

    async def record_plugin_info(self, plugin_info: Dict[str, str]) -> None:
        """记录插件信息

        :param plugin_info: 插件信息
        """
        with open(self.__info_path, 'r') as f:
            plugin_infos: List[Dict] = json.load(f)
        if local_plugin_info := await self.get_plugin_info(plugin_info):
            plugin_infos.remove(local_plugin_info[0])
        plugin_infos.append(plugin_info)
        with open(self.__info_path, 'w') as f:
            json.dump(plugin_infos, f, indent=4, ensure_ascii=False)

    async def remove_plugin_info(self, plugin_info: Dict[str, str]) -> None:
        """删除插件信息

        :param plugin_info: 插件信息
        """
        with open(self.__info_path, 'r') as f:
            plugin_infos: List[Dict] = json.load(f)
        if local_plugin_info := await self.get_plugin_info(plugin_info):
            plugin_infos.remove(local_plugin_info[0])
        with open(self.__info_path, 'w') as f:
            json.dump(plugin_infos, f, indent=4, ensure_ascii=False)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    async def get_remote_plugins(self, info: str = 'list.json') -> List:
        """获取远程插件信息

        :param info: 插件信息文件名
        """
        await asyncio.sleep(1)
        return json.loads(await general_request(self.__base_url + info, method='get'))

    async def get_plugin_by_url(self, root_dir, url_lists) -> bool:
        """通过远程插件地址获取插件

        :param root_dir: 插件所在目录
        :param url_lists: 插件资源列表
        """
        for url in url_lists:
            Path(f"{self.__folder_path}/{root_dir}{''.join(f'/{i}' for i in url.split('/')[:-1])}").mkdir(
                parents=True, exist_ok=True)
            filepath = self.__folder_path.joinpath(f'{root_dir}/{url}')
            await asyncio.sleep(1)
            if not await to_thread(download, self.__base_url + f'{root_dir}/{url}', filepath):
                return False
        return True

    async def install_plugin(self, plugin_info: Dict[str, str]) -> bool:
        """安装插件

        :param plugin_info: 插件信息
        """
        logger.info(f"正在尝试安装插件: {plugin_info['name']} - {plugin_info['author']}")
        resource_urls: list = await self.get_remote_plugins(f'{plugin_info["root_dir"]}/resource.json')
        if plugin_info['pypi']:
            resource_urls.append('requirements.txt')
        if await self.get_plugin_by_url(plugin_info['root_dir'], resource_urls):
            if plugin_info['pypi']:
                await to_thread(
                    pip, ['install',
                          '-r', str(self.__folder_path.joinpath(f"{plugin_info['root_dir']}/requirements.txt")),
                          '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple']
                )
            plugins = {}
            for plugin in self.__folder_path.joinpath(plugin_info['root_dir']).rglob(pattern='*.py'):
                if plugin.name not in self.__ignore and plugin.is_file():
                    plugin_name = f"{plugin.parent.name}.{plugin.name.split('.')[0]}"
                    plugins.update({plugin_name: PluginType.Extension})
            await self.loads_plugin(plugins)
            await self.record_plugin_info(plugin_info)
            logger.success(f"插件安装成功: {plugin_info['name']} - {plugin_info['author']}")
            return True
        else:
            logger.error(f"插件安装失败，请尝试重新安装: {plugin_info['name']} - {plugin_info['author']}")
            return False

    def delete_plugin(self, plugin_info: Dict[str, str]) -> None:
        """删除插件

        仅支持删除扩展插件

        :param plugin_info: 插件信息
        """
        self.unload_plugin(plugin_info['root_dir'])
        shutil.rmtree(self.__folder_path.joinpath(plugin_info['root_dir']))
        asyncio.create_task(self.remove_plugin_info(plugin_info))
        logger.success(f"插件删除成功: {plugin_info['name']} - {plugin_info['author']}")

    async def check_update(self) -> Union[None, bytes]:
        """检查更新"""
        local_plugins = await self.get_plugin_info('*')
        if not local_plugins:
            return
        remote_plugins = await self.get_remote_plugins()
        is_update = False
        msg = PrettyTable()
        msg.field_names = ['插件名', '作者', '当前版本', '最新版本']
        for local_plugin in local_plugins:
            for remote_plugin in remote_plugins:
                if local_plugin['name'] == remote_plugin['name'] and local_plugin['author'] == remote_plugin['author']:
                    if compare_version(remote_plugin['version'], local_plugin['version']):
                        is_update = True
                        msg.add_row([local_plugin['name'], local_plugin['author'], local_plugin['version'],
                                     remote_plugin['version']])
                        break
        if is_update:
            return await create_image(msg.get_string(), cut=150)
