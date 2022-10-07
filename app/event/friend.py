from datetime import datetime
from typing import Optional

from graia.ariadne.event.message import FriendMessage
from graia.ariadne.event.mirai import NewFriendRequestEvent

from app.core.app import AppCore
from app.core.settings import ADMIN_USER, config
from app.util.graia import Ariadne, Forward, ForwardNode, MessageChain, Plain, message

core: AppCore = AppCore()
bcc = core.get_bcc()
inc = core.get_inc()


@bcc.receiver(NewFriendRequestEvent)
async def new_friend_request(app: Ariadne, event: NewFriendRequestEvent):
    """收到好友申请"""
    source_group: Optional[int] = event.source_group
    group_name = "未知"
    if source_group:
        group_name = await app.get_group(source_group)
        if group_name:
            group_name = group_name.name
    for qq in ADMIN_USER:
        message(
            [
                Plain("收到添加好友事件\r\n"),
                Plain(f"QQ: {event.supplicant}\r\n"),
                Plain(f"昵称: {event.nickname}\r\n"),
                Plain(f"来自群: {group_name}({source_group})\r\n") if source_group else Plain("来自好友搜索\r\n"),
                Plain("状态: 已通过申请\r\n"),
                Plain(event.message) if event.message else Plain("无附加信息"),
            ]
        ).target(qq).send()
    await event.accept()


@bcc.receiver(FriendMessage)
async def friend_message(event: FriendMessage):
    """收到好友消息"""
    if event.sender.id != config.MASTER_QQ:
        message(
            Forward(
                [
                    ForwardNode(
                        target=event.sender,
                        time=datetime.now(),
                        message=MessageChain(f"收到来自{event.sender.nickname} - {event.sender.id}的消息"),
                    ),
                    ForwardNode(target=event.sender, time=datetime.now(), message=event.message_chain.as_sendable()),
                ]
            )
        ).target(config.MASTER_QQ).send()
