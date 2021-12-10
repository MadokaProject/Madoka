from typing import Optional

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.core.settings import ADMIN_USER
from app.event.base import Event


class NewFriendRequest(Event):
    """收到好友申请"""
    event_name = 'NewFriendRequestEvent'

    async def process(self):
        sourceGroup: Optional[int] = self.new_friend.sourceGroup
        if sourceGroup:
            group_name = await self.app.getGroup(sourceGroup)
            if group_name:
                group_name = group_name.name
            else:
                group_name = '未知'
        for qq in ADMIN_USER:
            await self.app.sendFriendMessage(qq, MessageChain.create([
                Plain("收到添加好友事件\r\n"),
                Plain(f"QQ: {self.new_friend.supplicant}\r\n"),
                Plain(f"昵称: {self.new_friend.nickname}\r\n"),
                Plain(f"来自群: {group_name}({sourceGroup})\r\n") if sourceGroup else Plain("来自群搜索\r\n"),
                Plain("状态: 已通过申请\r\n"),
                Plain(self.new_friend.message) if self.new_friend.message else Plain("无附加信息")
            ]))
        await self.new_friend.accept()
