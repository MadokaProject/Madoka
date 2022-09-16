import asyncio
import contextlib
import importlib
import sys

from creart import it
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import HttpClientConfig, WebsocketClientConfig
from graia.ariadne.connection.config import config as cfg
from graia.ariadne.console import Console
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from graia.scheduler import GraiaScheduler
from loguru import logger
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from app.core.config import Config
from app.core.exceptions import AppCoreNotInitializedError, AriadneAlreadyLaunchedError
from app.extend.power import power
from app.util.decorator import Singleton


class AppCore(metaclass=Singleton):
    __app: Ariadne = None
    __console: Console = None
    __bcc: Broadcast = None
    __inc: InterruptControl = None
    __scheduler: GraiaScheduler = None
    __thread_pool = None
    __config: Config = Config()
    __launched: bool = False
    __group_handler_chain = {}

    def __init__(self):
        logger.info("Madoka is starting")
        logger.info("Initializing")
        self.__bcc = it(Broadcast)
        host = f"http://{self.__config.LOGIN_HOST}:{self.__config.LOGIN_PORT}"
        app_config = cfg(
            self.__config.LOGIN_QQ,
            self.__config.VERIFY_KEY,
            HttpClientConfig(host),
            WebsocketClientConfig(host),
        )
        self.__app = Ariadne(app_config)
        self.__inc = InterruptControl(self.__bcc)
        self.__scheduler = self.__app.create(GraiaScheduler)
        self.__console = Console(
            broadcast=self.__bcc,
            prompt=HTML("<split_1></split_1><madoka> Madoka </madoka><split_2></split_2> "),
            style=Style(
                [
                    ("split_1", "fg:#61afef"),
                    ("madoka", "bg:#61afef fg:#ffffff"),
                    ("split_2", "fg:#61afef"),
                ]
            ),
        )
        logger.info("Initialize end")

    def get_app(self) -> Ariadne:
        if self.__app:
            return self.__app
        else:
            raise AppCoreNotInitializedError()

    def get_bcc(self) -> Broadcast:
        if self.__bcc:
            return self.__bcc
        else:
            raise AppCoreNotInitializedError()

    def get_inc(self):
        if self.__inc:
            return self.__inc
        else:
            raise AppCoreNotInitializedError()

    def get_scheduler(self):
        if self.__scheduler:
            return self.__scheduler
        raise AppCoreNotInitializedError()

    def get_console(self) -> Console:
        if self.__console:
            return self.__console
        else:
            raise AppCoreNotInitializedError()

    def get_config(self):
        return self.__config

    def launch(self):
        if not self.__launched:
            self.__launched = True
            with contextlib.suppress(KeyboardInterrupt, asyncio.exceptions.CancelledError):
                self.__app.launch_blocking()
            logger.info("Madoka is shutting down...")
        else:
            raise AriadneAlreadyLaunchedError()

    def set_group_chain(self, chains: list):
        for chain in chains:
            self.__group_handler_chain[chain.__name__] = chain

    def get_group_chains(self):
        return self.__group_handler_chain

    def get_group_chain(self, chain_name: str):
        return self.__group_handler_chain[chain_name] if chain_name in self.__group_handler_chain else None

    async def bot_launch_init(self):
        try:
            from app.core.plugins import PluginManager

            plg_mgr = PluginManager()
            await plg_mgr.loads_all()
            importlib.__import__("app.console.loads")
            importlib.__import__("app.core.event")
            importlib.__import__("app.extend.schedule")
            asyncio.create_task(power(self.__app, sys.argv))
            # if self.__config.WEBSERVER_ENABLE:
            #     logger.success("WebServer is starting")
            #     threading.Thread(daemon=True, target=WebServer).start()
            group_list = await self.__app.get_group_list()
            logger.info("本次启动活动群组如下：")
            for group in group_list:
                logger.info(f"群ID: {str(group.id).ljust(14)}群名: {group.name}")

            logger.success("Madoka is ready")
        except Exception as e:
            logger.exception(e)
            self.__app.stop()
