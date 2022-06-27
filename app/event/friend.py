from typing import Optional

from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import NewFriendRequestEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.core.app import AppCore
from app.core.settings import ADMIN_USER

core: AppCore = AppCore.get_core_instance()
bcc = core.get_bcc()
inc = core.get_inc()


@bcc.receiver(NewFriendRequestEvent)
async def new_friend_request(app: Ariadne, event: NewFriendRequestEvent):
    """收到好友申请"""
    source_group: Optional[int] = event.source_group
    group_name = '未知'
    if source_group:
        group_name = await app.get_group(source_group)
        if group_name:
            group_name = group_name.name
    for qq in ADMIN_USER:
        await app.send_friend_message(qq, MessageChain([
            Plain("收到添加好友事件\r\n"),
            Plain(f"QQ: {event.supplicant}\r\n"),
            Plain(f"昵称: {event.nickname}\r\n"),
            Plain(f"来自群: {group_name}({source_group})\r\n") if source_group else Plain("来自好友搜索\r\n"),
            Plain("状态: 已通过申请\r\n"),
            Plain(event.message) if event.message else Plain("无附加信息")
        ]))
    await event.accept()
