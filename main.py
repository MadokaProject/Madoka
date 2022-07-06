from pathlib import Path

from graia.ariadne.app import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.ariadne.model import Friend, Group, Member
from loguru import logger

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.core.controller import Controller
from app.util.other import online_notice, offline_notice
from app.util.version import version_notice

config = Config()

LOG_PATH = Path(__file__).parent.joinpath("app/tmp/logs")
LOG_PATH.mkdir(parents=True, exist_ok=True)
logger.add(LOG_PATH.joinpath("common.log"), level="INFO", retention=f"{config.COMMON_RETENTION} days", encoding="utf-8")
logger.add(LOG_PATH.joinpath("error.log"), level="ERROR", retention=f"{config.ERROR_RETENTION} days", encoding="utf-8")

core = AppCore()

app = core.get_app()
bcc = core.get_bcc()
inc = core.get_inc()
manager = CommandDelegateManager()


@bcc.receiver(FriendMessage)
async def friend_message_handler(_app: Ariadne, message: MessageChain, friend: Friend):
    await Controller(_app, message, friend, inc, manager).process_event()


@bcc.receiver(GroupMessage)
async def group_message_handler(_app: Ariadne, message: MessageChain, group: Group, member: Member, source: Source):
    await Controller(_app, message, group, member, source, inc, manager).process_event()


@logger.catch
@bcc.receiver(ApplicationLaunched)
async def init():
    await core.bot_launch_init()
    await online_notice(app, config)
    await version_notice(app, config)


@logger.catch
@bcc.receiver(ApplicationShutdowned)
async def stop():
    await offline_notice(app, config)


core.launch()
