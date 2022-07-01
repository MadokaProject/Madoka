from typing import List, Union

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, Group, Member

from app.util.control import Permission
from app.util.tools import parse_args


class Trigger:
    enable = True
    as_last = False

    def __init__(
            self,
            app: Ariadne,
            target: Union[Friend, Member],
            sender: Union[Friend, Group],
            message: MessageChain
    ):
        """根据需求可重写此构造方法"""
        self.app = app
        self.target = target
        self.sender = sender
        self.message: MessageChain = message
        self.msg: List[str] = parse_args(message.display, keep_head=True)
        self.resp = None

    async def process(self):
        raise NotImplementedError

    async def do_send(self, resp):
        """发送消息"""
        if not isinstance(resp, MessageChain):
            return
        if hasattr(self, 'friend'):  # 发送好友消息
            await self.app.send_friend_message(self.friend, resp)
        elif hasattr(self, 'group'):  # 发送群聊消息
            await self.app.send_group_message(self.group, resp)

    def check_admin(self, level: int):
        """检查是否管理员"""
        if Permission.require(self.target, level):
            return True
        return False

    def not_admin(self):
        return
