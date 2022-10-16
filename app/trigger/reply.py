from app.core.config import Config
from app.trigger.trigger import Trigger
from app.util.graia import At, Group, MessageChain, Plain
from app.util.online_config import get_config


class Reply(Trigger):
    """自定义消息回复"""

    async def process(self):
        if not isinstance(self.sender, Group) or self.msg[0][0] in Config.command.headers:
            return
        res = await get_config("group_reply", self.sender.id)
        message = self.message.display
        if res := res.get(message, None):
            await self.do_send(MessageChain([At(self.target), Plain(f" {res}")]))
            self.as_last = True
