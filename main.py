import asyncio
import sys
from pathlib import Path

from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import NewFriendRequestEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.ariadne.model import Friend, Group, Member, MiraiSession
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from graia.scheduler import GraiaScheduler
from loguru import logger

from app.core.config import Config
from app.core.controller import Controller
from app.event.friendRequest import FriendRequest
from app.event.join import Join
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


@bcc.receiver("MemberJoinEvent")
async def group_join_listener(group: Group, member: Member, app: Ariadne):
    event = Join(group, member, app)
    await event.process_event()


@bcc.receiver("NewFriendRequestEvent")
async def friend_request_listener(app: Ariadne, event: NewFriendRequestEvent):
    event = FriendRequest(app, event)
    await event.process_event()


if not config.DEBUG or not config.ONLINE:
    asyncio.run(custom_schedule(loop, bcc, bot))

loop.create_task(power(bot, sys.argv))
loop.run_until_complete(bot.lifecycle())
