from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.model import Group

from app.trigger.trigger import Trigger
from app.util.online_config import get_config


class Reply(Trigger):
    """自定义消息回复"""

    async def process(self):
        if not isinstance(self.sender, Group) or self.msg[0][0] in ".,;!?。，；！？/\\":
            return
        res = await get_config("group_reply", self.sender.id)
        message = self.message.display
        if res and res.__contains__(message):
            await self.do_send(MessageChain([At(self.target), Plain(f" {res[message]}")]))
            self.as_last = True
