import asyncio
import importlib
import os
import sys
import threading
import traceback
from asyncio.events import AbstractEventLoop
from pathlib import Path
from typing import List
from types import ModuleType

from graia.ariadne.adapter import DefaultAdapter
from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.model import MiraiSession
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from graia.scheduler import GraiaScheduler
from loguru import logger
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from app.core.Exceptions import *
from app.core.commander import CommandDelegateManager, command_manager
from app.core.config import Config
from app.extend.power import power
from app.extend.schedule import custom_schedule, TaskerProcess
from app.util.initDB import InitDB
from app.util.tools import app_path
from webapp.main import WebServer


class AppCore:
    __instance = None
    __first_init: bool = False
    __app: Ariadne = None
    __console: Console = None
    __loop: AbstractEventLoop = None
    __bcc: Broadcast = None
    __inc: InterruptControl = None
    __scheduler: GraiaScheduler = None
    __manager = None
    __plugin: List[ModuleType] = []
    __thread_pool = None
    __config: Config = None
    __launched: bool = False
    __group_handler_chain = {}
    __basic = [
        'sys',
        'power',
        'accountManager',
        'madoka_manager',
        'csm',
        'permission',
        'replyKeyword',
        'GroupJoin',
        'GithubListener',
        'mcinfo',
        'game',
        'rank'
    ]

    def __new__(cls, config: Config):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, config: Config):
        if not self.__first_init:
            logger.info("Madoka is starting")
            logger.info("Initializing")
            self.__loop = asyncio.get_event_loop()
            self.__bcc = Broadcast(loop=self.__loop)
            self.__app = Ariadne(
                broadcast=self.__bcc,
                connect_info=DefaultAdapter(
                    broadcast=self.__bcc,
                    mirai_session=MiraiSession(
                        host=f'http://{config.LOGIN_HOST}:{config.LOGIN_PORT}',
                        verify_key=config.VERIFY_KEY,
                        account=config.LOGIN_QQ
                    ),
                    log=config.HEARTBEAT_LOG
                ),
                chat_log_config=False
            )
            self.__inc = InterruptControl(self.__bcc)
            self.__scheduler = GraiaScheduler(loop=self.__loop, broadcast=self.__bcc)
            self.__app.debug = False
            self.__config = config
            self.__console = Console(
                broadcast=self.__bcc,
                prompt=HTML('<split_1></split_1><madoka> Madoka </madoka><split_2></split_2> '),
                style=Style(
                    [
                        ('split_1', 'fg:#61afef'),
                        ('madoka', 'bg:#61afef fg:#ffffff'),
                        ('split_2', 'fg:#61afef'),
                    ]
                )
            )
            self.__manager = command_manager
            AppCore.__first_init = True
            logger.info("Initialize end")
        else:
            raise AppCoreAlreadyInitialized()

    @classmethod
    def get_core_instance(cls):
        if cls.__instance:
            return cls.__instance
        else:
            raise AppCoreNotInitialized()

    def get_bcc(self) -> Broadcast:
        if self.__bcc:
            return self.__bcc
        else:
            raise AppCoreNotInitialized()

    def get_loop(self) -> AbstractEventLoop:
        if self.__loop:
            return self.__loop
        else:
            raise AppCoreNotInitialized()

    def get_app(self) -> Ariadne:
        if self.__app:
            return self.__app
        else:
            raise AppCoreNotInitialized()

    def get_console(self) -> Console:
        if self.__console:
            return self.__console
        else:
            raise AppCoreNotInitialized()

    def get_inc(self):
        return self.__inc

    def get_manager(self) -> CommandDelegateManager:
        if self.__manager:
            return self.__manager
        else:
            raise CommandManagerInitialized

    def get_plugin(self) -> List[ModuleType]:
        if self.__plugin:
            return self.__plugin
        else:
            raise PluginNotInitialized()

    def get_config(self):
        return self.__config

    def launch(self):
        if not self.__launched:
            self.__app.launch_blocking()
            self.__launched = True
        else:
            raise AriadneAlreadyLaunched()

    def set_group_chain(self, chains: list):
        for chain in chains:
            self.__group_handler_chain[chain.__name__] = chain

    def get_group_chains(self):
        return self.__group_handler_chain

    def get_group_chain(self, chain_name: str):
        return self.__group_handler_chain[chain_name] if chain_name in self.__group_handler_chain else None

    async def bot_launch_init(self):
        try:
            threading.Thread(daemon=True, target=WebServer).start()
            await InitDB(self.__basic)
            self.__loop.create_task(power(self.__app, sys.argv))
            group_list = await self.__app.getGroupList()
            logger.info("本次启动活动群组如下：")
            for group in group_list:
                logger.info(f"群ID: {str(group.id).ljust(14)}群名: {group.name}")

            logger.success("WebServer is starting")
            importlib.__import__("app.core.eventCore")
            importlib.__import__("app.core.console")
        except:
            logger.error(traceback.format_exc())
            exit()

    def load_plugin_modules(self):
        """加载全部插件"""

        def load_basic_plugin():
            """加载基础插件"""
            for plugin in self.__basic:
                try:
                    module = importlib.import_module(f"app.plugin.basic.{plugin}")
                    self.__plugin.append(module)
                    logger.success("成功加载系统插件: " + module.__name__)
                except ModuleNotFoundError as e:
                    logger.error(f"plugin 模块: {plugin} - {e}")

        def load_extension_plugin():
            """加载扩展插件"""
            for plugin in os.listdir(os.path.join(app_path(), "plugin/extension")):
                try:
                    if plugin not in ignore and plugin.split('.')[-1] == 'py' and not os.path.isdir(plugin):
                        module = importlib.import_module(f"app.plugin.extension.{plugin.split('.')[0]}")
                        if hasattr(module, 'Module'):
                            self.__plugin.append(module)
                            logger.success("成功加载插件: " + module.__name__)
                except ModuleNotFoundError as e:
                    logger.error(f"plugin 模块: {plugin} - {e}")

        ignore = ["__init__.py", "__pycache__"]
        self.__plugin.clear()
        load_basic_plugin()
        Path(app_path() + "/plugin/extension").mkdir(exist_ok=True)
        load_extension_plugin()

    def reload_plugin_modules(self, plugin='all_plugin') -> str:
        """重载插件

        :param plugin: 指定插件名
        """
        if plugin == 'all_plugin':
            for module in self.__plugin:
                self.__manager.delete(module)
                importlib.reload(module)
            return '重载成功'
        for module in self.__plugin:
            if plugin == str(module.__name__).split('.')[-1]:
                self.__manager.delete(module)
                importlib.reload(module)
                return f'{plugin} 重载成功'
        return '重载失败，无此插件！'

    async def load_plugin(self, plugin_name: str):
        """加载插件"""
        try:
            plugin_name = 'app.plugin.extension.' + plugin_name
            if not await self.fild_plugin(plugin_name):
                plugin: ModuleType = importlib.import_module(plugin_name)
                if hasattr(plugin, 'Module'):
                    self.__plugin.append(plugin)
                    logger.success("成功加载插件: " + plugin.__name__)
                    return "加载扩展插件成功: " + plugin.__name__
                else:
                    return '这或许不是一个插件？'
            else:
                return '该扩展插件已加载!'
        except ModuleNotFoundError as e:
            logger.error(f"扩展插件加载失败: {e}")
            return f'扩展插件加载失败: {e}'

    def unload_plugin(self, plugin_name):
        """卸载插件"""
        plugin_name = 'app.plugin.extension.' + plugin_name
        if plugin_name in sys.modules.keys():
            sys.modules.pop(plugin_name)
            for __plugin in self.__plugin:
                if plugin_name == __plugin.__name__:
                    self.__manager.delete(__plugin)
                    self.__plugin.remove(__plugin)
            return '卸载扩展插件成功: ' + plugin_name
        return '该扩展插件未加载'

    async def fild_plugin(self, plugin: str) -> bool:
        """查找插件是否加载"""
        for __plugin in self.__plugin:
            if plugin == __plugin.__name__:
                return True
        return False

    def load_schedulers(self):
        """加载计划任务"""
        tasks = []
        ignore = ["__init__.py", "__pycache__", "base.py"]
        for __dir in ['basic', 'extension']:
            for __scheduler in os.listdir(os.path.join(app_path(), f"plugin/{__dir}")):
                try:
                    if __scheduler not in ignore and __scheduler.split('.')[-1] == 'py' and not os.path.isdir(
                            __scheduler):
                        module = importlib.import_module(f"app.plugin.{__dir}.{__scheduler.split('.')[0]}")
                        if hasattr(module, "Tasker"):
                            obj = module.Tasker(self.__app)
                            if obj.cron:
                                tasks.append(TaskerProcess(self.__scheduler, obj))
                                logger.success("成功加载计划任务: " + module.__name__)
                except ModuleNotFoundError as e:
                    logger.error(f"schedule 模块: {__scheduler} - {e}")
        asyncio.gather(*tasks)
        asyncio.run(custom_schedule(self.__scheduler, self.__app))
