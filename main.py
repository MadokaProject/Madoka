import asyncio
import sys
from pathlib import Path

from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import (
    NewFriendRequestEvent,
    NudgeEvent,
    BotInvitedJoinGroupRequestEvent,
    BotJoinGroupEvent,
    BotLeaveEventKick,
    BotLeaveEventActive,
    BotGroupPermissionChangeEvent,
    BotMuteEvent,
    MemberCardChangeEvent,
    MemberJoinEvent,
    MemberLeaveEventKick,
    MemberLeaveEventQuit,
    MemberHonorChangeEvent,
)
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.ariadne.model import Friend, Group, Member, MiraiSession
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from graia.scheduler import GraiaScheduler
from loguru import logger

from app.core.config import Config
from app.core.controller import Controller
from app.event.event import EventController
from app.extend.power import power
from app.extend.schedule import custom_schedule
from initDB import initDB

LOG_PATH = Path("./app/tmp/logs")
LOG_PATH.mkdir(parents=True, exist_ok=True)
logger.add(
    LOG_PATH.joinpath("latest.log"),
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
    rotation="00:00",
    retention="30 days",
    compression="tar.xz",
    colorize=False,
)
logger.info("PyIBot is starting...")

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
config = Config()
bot = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host='http://' + config.LOGIN_HOST + ':' + config.LOGIN_PORT,
        verify_key=config.VERIFY_KEY,
        account=config.LOGIN_QQ
    )
)
scheduler = GraiaScheduler(
    loop, bcc
)

inc: InterruptControl = InterruptControl(bcc)

if not asyncio.run(initDB()):  # 初始化数据库
    logger.error('初始化数据库失败')
    exit(-3306)


@bcc.receiver("FriendMessage")
async def friend_message_listener(message: MessageChain, friend: Friend, app: Ariadne):
    event = Controller(message, friend, app)
    await event.process_event()


@bcc.receiver("GroupMessage")
async def group_message_listener(message: MessageChain, group: Group, member: Member, app: Ariadne, source: Source):
    event = Controller(message, group, member, app, source, inc)
    await event.process_event()


@bcc.receiver("ApplicationLaunched")
async def application_launched(app: Ariadne):
    event = EventController("ApplicationLaunched", app, inc)
    await event.process_event()


@bcc.receiver("ApplicationShutdowned")
async def application_showdown_listener(app: Ariadne):
    event = EventController("ApplicationShutdowned", app, inc)
    await event.process_event()


@bcc.receiver("NewFriendRequestEvent")
async def new_friend_request_listener(app: Ariadne, event: NewFriendRequestEvent):
    event = EventController("NewFriendRequestEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("NudgeEvent")
async def nudge_listener(app: Ariadne, event: NudgeEvent):
    print('戳一戳')
    event = EventController("NudgeEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("BotInvitedJoinGroupRequestEvent")
async def bot_invited_join_group_request_listener(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    event = EventController("BotInvitedJoinGroupRequestEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("BotJoinGroupEvent")
async def bot_join_group_listener(app: Ariadne, event: BotJoinGroupEvent):
    event = EventController("BotJoinGroupEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("BotLeaveEventKick")
async def bot_leave_kick_listener(app: Ariadne, event: BotLeaveEventKick):
    event = EventController("BotLeaveEventKick", app, inc, event)
    await event.process_event()


@bcc.receiver("BotLeaveEventActive")
async def bot_leave_active_listener(app: Ariadne, event: BotLeaveEventActive):
    event = EventController("BotLeaveEventActive", app, inc, event)
    await event.process_event()


@bcc.receiver("BotGroupPermissionChangeEvent")
async def bot_group_permission_change_listener(app: Ariadne, event: BotGroupPermissionChangeEvent):
    event = EventController("BotGroupPermissionChangeEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("BotMuteEvent")
async def bot_mute_listener(app: Ariadne, event: BotMuteEvent):
    event = EventController("BotMuteEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberCardChangeEvent")
async def member_card_change_listener(app: Ariadne, event: MemberCardChangeEvent):
    event = EventController("MemberCardChangeEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberJoinEvent")
async def member_join_listener(app: Ariadne, event: MemberJoinEvent):
    event = EventController("MemberJoinEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberLeaveEventKick")
async def member_leave_kick_listener(app: Ariadne, event: MemberLeaveEventKick):
    event = EventController("MemberLeaveEventKick", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberLeaveEventQuit")
async def member_leave_quit_listener(app: Ariadne, event: MemberLeaveEventQuit):
    event = EventController("MemberLeaveEventQuit", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberHonorChangeEvent")
async def member_honor_change_listener(app: Ariadne, event: MemberHonorChangeEvent):
    event = EventController("MemberHonorChangeEvent", app, inc, event)
    await event.process_event()


if not config.DEBUG or not config.ONLINE:
    asyncio.run(custom_schedule(loop, bcc, bot))

loop.create_task(power(bot, sys.argv))
loop.run_until_complete(bot.lifecycle())
