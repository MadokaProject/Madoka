import random

from loguru import logger

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
        try:
            if (probability < 1) and repeated(self.group.id, self.app.account, 2):
                await self.app.sendGroupMessage(self.group, self.message.asSendable())
                save(self.group.id, self.app.account, self.message.asDisplay())
                logger.info('Random Repeat: ' + self.message.asDisplay())
            if repeated(self.group.id, self.app.account, 2):
                await self.app.sendGroupMessage(self.group, self.message.asSendable())
                save(self.group.id, self.app.account, self.message.asDisplay())
                logger.info('Follow Repeat: ' + self.message.asDisplay())
        except Exception as e:
            logger.warning(e)
