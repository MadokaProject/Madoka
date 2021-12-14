from pathlib import Path

from graia.ariadne.app import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.ariadne.model import Friend, Group, Member
from loguru import logger

from app.core.appCore import AppCore
from app.core.config import Config
from app.core.controller import Controller
from app.util.other import online_notice, offline_notice

config = Config()

LOG_PATH = Path("./app/tmp/logs")
LOG_PATH.mkdir(parents=True, exist_ok=True)
logger.add(LOG_PATH.joinpath("common.log"), level="INFO", retention=f"{config.COMMON_RETENTION} days", encoding="utf-8")
logger.add(LOG_PATH.joinpath("error.log"), level="ERROR", retention=f"{config.ERROR_RETENTION} days", encoding="utf-8")

core = AppCore(config)

core.load_plugin_modules()
core.load_schedulers()

app = core.get_app()
bcc = core.get_bcc()
inc = core.get_inc()


@bcc.receiver(FriendMessage)
async def friend_message_handler(app: Ariadne, message: MessageChain, friend: Friend):
    message_text_log = message.asDisplay().replace("\n", "\\n")
    logger.info(f"收到来自好友 <{friend.nickname}> 的消息：{message_text_log}")
    await Controller(core.get_plugin(), app, message, friend).process_event()


@bcc.receiver(GroupMessage)
async def group_message_handler(app: Ariadne, message: MessageChain, group: Group, member: Member, source: Source):
    message_text_log = message.asDisplay().replace("\n", "\\n")
    logger.info(f"收到来自群 <{group.name}> 中成员 <{member.name}> 的消息：{message_text_log}")
    await Controller(core.get_plugin(), app, message, group, member, source, inc).process_event()


@logger.catch
@bcc.receiver(ApplicationLaunched)
async def init():
    await core.bot_launch_init()
    await online_notice(app, config)


@logger.catch
@bcc.receiver(ApplicationShutdowned)
async def stop():
    await offline_notice(app, config)


core.launch()
