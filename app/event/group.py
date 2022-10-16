from datetime import datetime
from io import BytesIO

from graia.ariadne.event.mirai import (
    GroupRecallEvent,
    MemberCardChangeEvent,
    MemberHonorChangeEvent,
    MemberJoinEvent,
    MemberLeaveEventKick,
    MemberLeaveEventQuit,
)
from PIL import Image as IMG

from app.core.app import AppCore
from app.core.config import Config
from app.core.settings import ADMIN_USER
from app.util.graia import (
    Ariadne,
    At,
    Forward,
    ForwardNode,
    Image,
    MemberInfo,
    MessageChain,
    Plain,
    message,
)
from app.util.network import general_request
from app.util.online_config import get_config

core: AppCore = AppCore()
bcc = core.get_bcc()
inc = core.get_inc()


async def avatar_black_and_white(qq: int) -> bytes:
    """
    获取群成员头像黑白化
    """
    url = f"https://q1.qlogo.cn/g?b=qq&nk={qq}&s=4"
    resp = await general_request(url, _type="byte")
    img = IMG.open(BytesIO(resp))
    img = img.convert("L")
    img.save(img2io := BytesIO(), "JPEG")
    return img2io.getvalue()


@bcc.receiver(MemberCardChangeEvent)
async def card_change(app: Ariadne, event: MemberCardChangeEvent):
    """群名片被修改"""
    if event.member.id == Config.bot.account:
        if event.current != Config.name:
            for qq in ADMIN_USER:
                message(
                    [
                        Plain(f"检测到 {Config.name} 群名片变动"),
                        Plain(f"\n群号：{event.member.group.id}"),
                        Plain(f"\n群名：{event.member.group.name}"),
                        Plain(f"\n被修改为：{event.current}"),
                        Plain(f"\n已为你修改回：{Config.name}"),
                    ]
                ).target(qq).send()
            await app.modify_member_info(
                group=event.member.group.id,
                member=Config.bot.account,
                info=MemberInfo(name=Config.name),
            )
            message("请不要修改我的群名片").target(event.member.group).send()
    elif await get_config("member_card_change", event.member.group.id) and event.current not in [None, ""]:
        message(
            [
                At(event.member.id),
                Plain(f" 的群名片由 {event.origin} 被修改为 {event.current}"),
            ]
        ).target(event.member.group).send()


@bcc.receiver(MemberJoinEvent)
async def join(event: MemberJoinEvent):
    """有人加入群聊"""
    msg = [
        Image(url=f"https://q1.qlogo.cn/g?b=qq&nk={event.member.id}&s=4"),
        Plain("\n欢迎 "),
        At(event.member.id),
        Plain(" 加入本群"),
    ]
    res = await get_config("member_join", event.member.group.id)
    if res and res["active"]:
        msg.append(Plain(f"\r\n{res['text']}") if "text" in res else None)
        message(msg).target(event.member.group).send()


@bcc.receiver(MemberLeaveEventKick)
async def leave_kick(event: MemberLeaveEventKick):
    """有人被踢出群聊"""
    msg = [
        Image(data_bytes=await avatar_black_and_white(event.member.id)),
        Plain(f"\n{event.member.name} 被 "),
        At(event.operator.id) if event.operator else Plain(Config.name),
        Plain(" 踢出本群"),
    ]
    if await get_config("member_kick", event.member.group.id):
        message(msg).target(event.member.group).send()


@bcc.receiver(MemberLeaveEventQuit)
async def leave_quit(event: MemberLeaveEventQuit):
    """有人退出群聊"""
    msg = [
        Image(data_bytes=await avatar_black_and_white(event.member.id)),
        Plain(f"\n{event.member.name} 退出本群"),
    ]
    if await get_config("member_quit", event.member.group.id):
        message(msg).target(event.member.group).send()


@bcc.receiver(MemberHonorChangeEvent)
async def honor_change(event: MemberHonorChangeEvent):
    """有人群荣誉变动"""
    msg = [
        At(event.member.id),
        Plain(f" {'获得了' if event.action == 'achieve' else '失去了'} 群荣誉 {event.honor}！"),
    ]
    message(msg).target(event.member.group).send()


@bcc.receiver(GroupRecallEvent)
async def recall(app: Ariadne, event: GroupRecallEvent):
    """有人撤回消息"""
    if event.operator is None:
        return
    if Config.event.groupRecall2me or await get_config("member_recall", event.group.id):
        msg = message(
            Forward(
                [
                    ForwardNode(
                        target=event.operator,
                        time=datetime.now(),
                        message=MessageChain(
                            f"{event.group.name}: {event.group.id} 群有人撤回了一条消息"
                            if Config.event.groupRecall2me
                            else "有人撤回了一条消息"
                        ),
                    ),
                    ForwardNode(
                        target=event.operator,
                        time=datetime.now(),
                        message=(
                            await app.get_message_from_id(event.message_id, event.group)
                        ).message_chain.as_sendable(),
                    ),
                ]
            )
        )
        if Config.event.groupRecall2me:
            msg.target(Config.master_qq).send()
        else:
            msg.target(event.group).send()
