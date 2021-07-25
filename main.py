import asyncio

from graia.application.entry import *
from graia.application.friend import Friend
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler
from graia.scheduler.timers import crontabify

from app.core.config import *
from app.core.controller import Controller
from app.event.join import Join
from app.extend.GroupTimingMessage import TimingMessage
from app.extend.NetEaseCloudMusicAction import NetEase_action
from app.extend.github import github_listener
from app.extend.schedule import custom_schedule
from auto_sql import auto_create_sql

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

auto_create_sql()  # 初始化数据库


@bcc.receiver("FriendMessage")
async def friend_message_listener(message: MessageChain, friend: Friend, app: GraiaMiraiApplication):
    event = Controller(message, friend, app)
    await event.process_event()


@bcc.receiver("GroupMessage")
async def group_message_listener(message: MessageChain, group: Group, member: Member, app: GraiaMiraiApplication):
    event = Controller(message, group, member, app)
    await event.process_event()


@bcc.receiver("MemberJoinEvent")
async def group_join_listener(group: Group, member: Member, app: GraiaMiraiApplication):
    event = Join(group, member, app)
    await event.process_event()


@bcc.receiver("NewFriendRequestEvent")
async def friend_request_listener(app: GraiaMiraiApplication, event: NewFriendRequestEvent):
    await event.accept()
    await app.sendFriendMessage(1332925715, MessageChain.create([
        Plain('有人申请加我为好友\r\n昵称: ' + event.nickname + '\r\nQQ: ' + str(
            event.supplicant) + '\r\n来自群聊: ' + str(event.sourceGroup) + '\r\n附加消息: ' + event.message + '\r\n已自动同意')
    ]))


@scheduler.schedule(crontabify("0 0 * * * "))
async def group_timing_message():
    await TimingMessage(app)


@scheduler.schedule(crontabify(REPO_TIME))
async def github_commit_listener():
    await github_listener(app)


@scheduler.schedule(crontabify("0 8 * * *"))
async def NetEase_actions():
    await NetEase_action(app)


asyncio.run(custom_schedule(loop, bcc, app))

app.launch_blocking()
loop.run_forever()
