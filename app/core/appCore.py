import asyncio
import importlib
import os
import sys
import traceback
from asyncio.events import AbstractEventLoop

from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from loguru import logger

try:
    from graia.scheduler import GraiaScheduler

    _install_scheduler = True
except (ModuleNotFoundError, ImportError):
    _install_scheduler = False

from app.core.config import Config
from app.extend.power import power
from app.extend.schedule import custom_schedule, TaskerProcess
from app.util.initDB import InitDB
from app.util.tools import app_path
from .Exceptions import *


class AppCore:
    __instance = None
    __first_init: bool = False
    __app: Ariadne = None
    __loop: AbstractEventLoop = None
    __bcc = None
    __inc = None
    __plugin = []
    __thread_pool = None
    __config: Config = None
    __launched: bool = False
    __group_handler_chain = {}

    def __new__(cls, config: Config):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, config: Config):
        if not self.__first_init:
            logger.info("Initializing")
            self.__loop = asyncio.get_event_loop()
            self.__bcc = Broadcast(loop=self.__loop)
            self.__app = Ariadne(
                broadcast=self.__bcc,
                connect_info=MiraiSession(
                    host=f'http://{config.LOGIN_HOST}:{config.LOGIN_PORT}',
                    verify_key=config.VERIFY_KEY,
                    account=config.LOGIN_QQ
                ),
                chat_log_config=False
            )
            self.__inc = InterruptControl(self.__bcc)
            if _install_scheduler:
                self.__sche = GraiaScheduler(loop=self.__loop, broadcast=self.__bcc)
            self.__app.debug = False
            self.__config = config
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

    def get_inc(self):
        return self.__inc

    def get_plugin(self) -> list:
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
            await InitDB()
            self.__loop.create_task(power(self.__app, sys.argv))
            group_list = await self.__app.getGroupList()
            logger.info("本次启动活动群组如下：")
            for group in group_list:
                logger.info(f"群ID: {str(group.id).ljust(14)}群名: {group.name}")

            importlib.__import__("app.core.eventCore")
        except:
            logger.error(traceback.format_exc())
            exit()

    def load_plugin_modules(self):
        ignore = ["__init__.py", "__pycache__", "base.py"]
        for plugin in os.listdir(os.path.join(app_path(), "plugin")):
            try:
                if plugin not in ignore and not os.path.isdir(plugin):
                    module = importlib.import_module(f"app.plugin.{plugin.split('.')[0]}")
                    if hasattr(module, 'Module'):
                        self.__plugin.append(module)
                        logger.success("成功加载插件: " + module.__name__)
            except ModuleNotFoundError as e:
                logger.error(f"plugin 模块: {plugin} - {e}")

    def load_schedulers(self):
        if not self.__config.DEBUG or not self.__config.ONLINE:
            tasks = []
            ignore = ["__init__.py", "__pycache__", "base.py"]
            for __scheduler in os.listdir(os.path.join(app_path(), "plugin")):
                try:
                    if __scheduler not in ignore and not os.path.isdir(__scheduler):
                        module = importlib.import_module(f"app.plugin.{__scheduler.split('.')[0]}")
                        if hasattr(module, "Tasker"):
                            obj = module.Tasker(self.__app)
                            if obj.cron:
                                tasks.append(TaskerProcess(self.__loop, self.__bcc, obj))
                                logger.success("成功加载计划任务: " + module.__name__)
                except ModuleNotFoundError as e:
                    logger.error(f"schedule 模块: {__scheduler} - {e}")
            asyncio.gather(*tasks)
            asyncio.run(custom_schedule(self.__loop, self.__bcc, self.__app))
