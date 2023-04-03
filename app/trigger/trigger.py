from typing import Union

from app.util.graia import Ariadne, Friend, Group, Member, MessageChain, Source, message
from app.util.tools import parse_args


class Trigger:
    enable = True
    as_last = False
    resp = None

    def __init__(
        self,
        app: Ariadne,
        target: Union[Friend, Member],
        sender: Union[Friend, Group],
        source: Source,
        message: MessageChain,
    ):
        """根据需求可重写此构造方法"""
        self.app = app
        self.target = target
        self.sender = sender
        self.source = source
        self.message = message
        self.msg: list[str] = parse_args(message.display, keep_head=True)

    async def process(self):
        raise NotImplementedError

    async def do_send(self, resp):
        """发送消息"""
        if not isinstance(resp, MessageChain):
            return
        message(resp).target(self.sender).send()

    def not_admin(self):
        return
