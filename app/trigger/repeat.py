import random

from app.trigger.trigger import Trigger
from app.util.msg import repeated, save


class Repeat(Trigger):
    """复读"""
    async def process(self):
        if not hasattr(self, 'group'):
            return
        if self.msg[0][0] in '.,;!?。，；！？/\\':  # 判断是否为指令
            return
        probability = random.randint(0, 101)
        if (probability < 1) and repeated(self.group.id, self.app.connect_info.account, 2):
            await self.app.sendGroupMessage(self.group, self.message.asSendable())
            save(self.group.id, self.app.connect_info.account, self.message.asDisplay())
            self.app.logger.info('Random Repeat: ' + self.message.asDisplay())
        if repeated(self.group.id, self.app.connect_info.account, 2):
            await self.app.sendGroupMessage(self.group, self.message.asSendable())
            save(self.group.id, self.app.connect_info.account, self.message.asDisplay())
            self.app.logger.info('Follow Repeat: ' + self.message.asDisplay())
