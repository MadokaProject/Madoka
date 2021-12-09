import asyncio
import sys

from graia.application.entry import *
from graia.application.friend import Friend
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler
from graia.broadcast.interrupt import InterruptControl
from loguru import logger
from pathlib import Path

from app.core.config import Config
from app.core.controller import Controller
from app.event.friendRequest import FriendRequest
from app.event.join import Join
from app.extend.power import power
from app.extend.schedule import custom_schedule
from initDB import initDB

LOGPATH = Path("./app/tmp/logs")
LOGPATH.mkdir(exist_ok=True)
logger.add(
    LOGPATH.joinpath("latest.log"),
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
bot = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host='http://' + config.LOGIN_HOST + ':' + config.LOGIN_PORT,
        authKey=config.AUTH_KEY,
        account=config.LOGIN_QQ,
        websocket=True
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
async def friend_message_listener(message: MessageChain, friend: Friend, app: GraiaMiraiApplication):
    event = Controller(message, friend, app)
    await event.process_event()


@bcc.receiver("GroupMessage")
async def group_message_listener(message: MessageChain, group: Group, member: Member, app: GraiaMiraiApplication, source: Source):
    event = Controller(message, group, member, app, source, inc)
    await event.process_event()


@bcc.receiver("MemberJoinEvent")
async def group_join_listener(group: Group, member: Member, app: GraiaMiraiApplication):
    event = Join(group, member, app)
    await event.process_event()


@bcc.receiver("NewFriendRequestEvent")
async def friend_request_listener(app: GraiaMiraiApplication, event: NewFriendRequestEvent):
    event = FriendRequest(app, event)
    await event.process_event()


if not config.DEBUG or not config.ONLINE:
    asyncio.run(custom_schedule(loop, bcc, bot))

loop.create_task(power(bot, sys.argv))
bot.launch_blocking()
