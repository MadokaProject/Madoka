import importlib
import json
import shutil
import sys
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Dict, Union

from graia.scheduler import GraiaScheduler
from loguru import logger
from pip import main as pip

from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.util.network import general_request, download
from app.util.tools import app_path, to_thread
from .exceptions import *


class PluginType(Enum):
    """描述插件类型"""
    Basic = "basic"  # 基础插件
    Extension = "extension"  # 扩展插件

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
    __basic = [
        'sys',
        'power',
        'account_manager',
        'madoka_manager',
        'csm',
        'permission',
        'reply_keyword',
        'group_join',
        'github_listener',
        'mc_info',
        'game',
        'rank'
    ]

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
            raise PluginManagerAlreadyInitialized("插件管理器重复初始化")

    @classmethod
    def get_instance(cls):
        if cls.__instance:
            return cls.__instance
        else:
            raise PluginManagerInitialized("插件管理器未初始化")

    def get_plugins(self):
        return self.__plugins

    async def load_plugin(self, plugin_name: str, plugin_type: PluginType = PluginType.Extension) -> bool:
        """加载插件

        :param plugin_name: 插件名
        :param plugin_type: 插件类型: Default: extension
        """
        try:
            plugin_name = f"app.plugin.{plugin_type}.{plugin_name}"
            if not await self.find_plugin(plugin_name):
                self.__plugins[plugin_name] = importlib.import_module(plugin_name)
                logger.success("成功加载插件: " + plugin_name)
                return True
            else:
                logger.warning('该插件已加载!')
                return True
        except ModuleNotFoundError as e:
            logger.error(f"插件加载失败: {plugin_name} - {e}")
            return False
        except ImportError as e:
            logger.error(f"插件加载失败: {plugin_name} - {e}")
            return False

    async def loads_plugin(self, plugins: Dict[str, PluginType]) -> Dict[str, bool]:
        """批量加载插件

        :param plugins: 批量加载的插件，{插件名: 插件类型}
        """
        result = {}
        for plugin_name, plugin_type in plugins.items():
            result.update({plugin_name: await self.load_plugin(plugin_name, plugin_type)})
        return result

    async def loads_basic_plugin(self) -> None:
        """加载基础插件"""
        await self.loads_plugin({plugin: PluginType.Basic for plugin in self.__basic})

    async def loads_extension_plugin(self) -> None:
        """加载扩展插件"""
        plugins = {}
        extension_plugin_path = self.__base_path.joinpath('extension')
        extension_plugin_path.mkdir(exist_ok=True)
        for plugin in extension_plugin_path.rglob(pattern='*.py'):
            if plugin.name not in self.__ignore and plugin.is_file():
                plugins.update({plugin.name.split('.')[0]: PluginType.Extension})
        await self.loads_plugin(plugins)

    async def loads_all_plugin(self) -> None:
        """加载所有插件（仅允许初始化时使用）"""
        self.__plugins.clear()
        await self.loads_basic_plugin()
        await self.loads_extension_plugin()

    def reload_plugin(self, plugin='all_plugin', plugin_type: PluginType = PluginType.Extension) -> bool:
        """重载插件

        :param plugin: 指定插件名
        :param plugin_type: 插件类型: Default: extension
        """
        if plugin == 'all_plugin':
            for module in self.__plugins.values():
                self.__manager.delete(module)
                self.remove_tasker(module)
                importlib.reload(module)
                logger.success(f"重载插件: {module.__name__} 成功")
            return True
        if module := self.__plugins.get(f'app.plugin.{plugin_type}.{plugin}'):
            self.__manager.delete(module)
            self.remove_tasker(module)
            importlib.reload(module)
            logger.success(f"重载插件: {module.__name__} 成功")
            return True
        logger.warning('重载失败，无此插件！')
        return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件
        仅支持卸载扩展插件
        """
        plugin_name = f"app.plugin.extension.{plugin_name}"
        if plugin_name in sys.modules.keys():
            sys.modules.pop(plugin_name)
            __plugin = self.__plugins.get(plugin_name)
            self.remove_tasker(__plugin)
            self.__manager.delete(__plugin)
            self.__plugins.pop(plugin_name)
            logger.success('卸载扩展插件成功: ' + plugin_name)
            return True
        logger.warning('该扩展插件未加载')
        return False

    def remove_tasker(self, tasks: ModuleType):
        """删除计划任务"""
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

    async def get_remote_plugins(self) -> dict:
        try:
            return json.loads(await general_request(self.__base_url + 'list.json', method='get'))
        except RuntimeError:
            try:
                return json.loads(await general_request(self.__base_url + 'list.json', method='get'))
            except RuntimeError:
                return json.loads(await general_request(self.__base_url + 'list.json', method='get'))

    async def get_plugin_by_url(self, plugin_name, url_lists) -> bool:
        if not await to_thread(download, self.__base_url + f'{plugin_name}/{plugin_name}.py',
                               self.__folder_path.joinpath(f'{plugin_name}.py')):
            return False
        for url in url_lists:
            Path(f"{self.__folder_path}/{plugin_name}_res{''.join(f'/{i}' for i in url.split('/')[:-1])}").mkdir(
                parents=True, exist_ok=True)
            filepath = self.__folder_path.joinpath(f'{plugin_name}_res/{url}')
            if not await to_thread(download, self.__base_url + f'{plugin_name}/{url}', filepath):
                return False
        return True

    async def install_plugin(self, plugin) -> bool:
        """安装插件

        :param plugin: 插件名
        """
        plugin_list = await self.get_remote_plugins()
        if plugin in plugin_list.keys():
            logger.info('正在尝试安装插件' + plugin_list[plugin]['name'])
            url_list = [i for i in plugin_list[plugin]['resource']]
            if plugin_list[plugin]['pypi']:
                url_list.append('requirements.txt')
            if await self.get_plugin_by_url(plugin, url_list):
                if plugin_list[plugin]['pypi']:
                    await to_thread(
                        pip, ['install',
                              '-r', str(self.__folder_path.joinpath(f'{plugin}_res/requirements.txt')),
                              '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple']
                    )
                await self.load_plugin(plugin, PluginType.Extension)
                logger.success('插件安装成功: ' + plugin)
                return True
            else:
                logger.error('插件安装失败，请尝试重新安装: ' + plugin_list[plugin]['name'])
                return False
        else:
            logger.warning('未找到该插件' + plugin)
            raise RemotePluginNotFound(plugin)

    def delete_plugin(self, plugin: str) -> bool:
        """删除插件

        :param plugin: 插件名（仅支持删除扩展插件）
        """
        if not self.__folder_path.joinpath(f'{plugin}.py').exists():
            return False
        self.unload_plugin(plugin)
        self.__folder_path.joinpath(f'{plugin}.py').unlink(missing_ok=True)
        __dir = self.__folder_path.joinpath(f'{plugin}/_res')
        if __dir.exists():
            shutil.rmtree(__dir)
        return True
