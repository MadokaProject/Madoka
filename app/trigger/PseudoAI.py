from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.trigger.trigger import Trigger


class PseudoAI(Trigger):
    async def process(self):
        if self.msg[0][0] in '.,;!?。，；！？/\\' or not hasattr(self, 'group'):  # 判断是否为指令
            return
        message = self.message.asDisplay()
        self.as_last = True
        if message[0:2] == '我不' and message[2] in ['要', '想', '会', '懂']:
            resp = MessageChain.create([
                Plain(message.replace('我不', '你'))
            ])
            await self.do_send(resp)
        elif message[0:2] in ['我要', '我想']:
            resp = MessageChain.create([
                Plain(message.replace('我', '你不'))
            ])
            await self.do_send(resp)
        else:
            self.as_last = False
