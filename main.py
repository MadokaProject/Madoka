import asyncio

from graia.application.entry import *
from graia.application.friend import Friend
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler
from graia.broadcast.interrupt import InterruptControl

from app.core.config import *
from app.core.controller import Controller
from app.event.friendRequest import FriendRequest
from app.event.join import Join
from app.extend.schedule import custom_schedule
from initDB import initDB

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host=HOST,  # 填入 httpapi 服务运行的地址
        authKey=AUTHKEY,  # 填入 authKey
        account=QQ,  # 你的机器人的 qq 号
        websocket=True  # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)
scheduler = GraiaScheduler(
    loop, bcc
)

inc: InterruptControl = InterruptControl(bcc)

if not asyncio.run(initDB()):  # 初始化数据库
    exit('初始化数据库失败')


@bcc.receiver("FriendMessage")
async def friend_message_listener(message: MessageChain, friend: Friend, app: GraiaMiraiApplication):
    event = Controller(message, friend, app)
    await event.process_event()


@bcc.receiver("GroupMessage")
async def group_message_listener(message: MessageChain, group: Group, member: Member, app: GraiaMiraiApplication,
                                 source: Source):
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


asyncio.run(custom_schedule(loop, bcc, app))

app.launch_blocking()
loop.run_forever()
