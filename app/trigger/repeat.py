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
                await self.app.send_group_message(self.group, self.message.as_sendable())
                save(self.group.id, self.app.account, self.message.display)
                logger.info('Random Repeat: ' + self.message.display)
            if repeated(self.group.id, self.app.account, 2):
                await self.app.send_group_message(self.group, self.message.as_sendable())
                save(self.group.id, self.app.account, self.message.display)
                logger.info('Follow Repeat: ' + self.message.display)
        except Exception as e:
            logger.warning(e)
