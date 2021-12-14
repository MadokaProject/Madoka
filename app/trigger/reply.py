from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At

from app.trigger.trigger import Trigger
from app.util.onlineConfig import get_config


class Reply(Trigger):
    """自定义消息回复"""

    async def process(self):
        if not hasattr(self, 'group'):
            return
        if self.msg[0][0] in '.,;!?。，；！？/\\':  # 判断是否为指令
            return
        res = await get_config('group_reply', self.group.id)
        message = self.message.asDisplay()
        if res and res.__contains__(message):
            await self.do_send(MessageChain.create([At(self.member.id), Plain(' ' + res[message])]))
            self.as_last = True
