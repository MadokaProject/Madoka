#!/usr/bin/env python
import contextlib
from pathlib import Path

from graia.ariadne.app import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.ariadne.model import Friend, Group, Member
from loguru import logger

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.core.controller import Controller
from app.core.exceptions import DependError
from app.extend.message_queue import mq
from app.util.other import offline_notice, online_notice
from app.util.version import version_notice

LOG_PATH = Path(__file__).parent.joinpath("app/tmp/logs")
LOG_PATH.mkdir(parents=True, exist_ok=True)
logger.add(
    LOG_PATH.joinpath("common.log"),
    level="INFO",
    rotation="2 days",
    retention="10 days",
    compression="zip",
    encoding="utf-8",
)
logger.add(
    LOG_PATH.joinpath("error.log"),
    level="ERROR",
    rotation="6 days",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
)

core = AppCore()

bcc = core.get_bcc()
inc = core.get_inc()
manager = CommandDelegateManager()


@bcc.receiver(FriendMessage)
async def friend_message_handler(app: Ariadne, message: MessageChain, friend: Friend):
    with contextlib.suppress(DependError):
        await Controller(app, message, friend, inc, manager).process_event()


@bcc.receiver(GroupMessage)
async def group_message_handler(app: Ariadne, message: MessageChain, group: Group, member: Member, source: Source):
    with contextlib.suppress(DependError):
        await Controller(app, message, group, member, source, inc, manager).process_event()


@logger.catch
@bcc.receiver(ApplicationLaunched)
async def init():
    await core.bot_launch_init()
    await online_notice()
    await version_notice()


@logger.catch
@bcc.receiver(ApplicationShutdowned)
async def stop():
    await offline_notice()
    await mq.stop()


core.launch()
