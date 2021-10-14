from graia.application import MessageChain
from graia.application.message.elements.internal import Plain

from app.trigger.trigger import Trigger


class PseudoAI(Trigger):
    async def process(self):
        if self.msg[0][0] in '.,;!?。，；！？/\\':  # 判断是否为指令
            return
        message = self.message.asDisplay()
        self.as_last = True
        if message[0:2] in '我不':
            resp = MessageChain.create([
                Plain(message.replace('我不', '你'))
            ])
            await self.do_send(resp)
        elif message[0:2] in ['我要', '我想', '我知道']:
            resp = MessageChain.create([
                Plain(message.replace('我', '你不'))
            ])
            await self.do_send(resp)
        else:
            self.as_last = False
