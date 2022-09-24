import random

from graia.ariadne.model import Group
from loguru import logger

from app.trigger.trigger import Trigger
from app.util.msg import repeated, save


class Repeat(Trigger):
    """复读"""

    async def process(self):
        if not isinstance(self.sender, Group):
            return
        if self.msg[0][0] in ".,;!?。，；！？/\\":  # 判断是否为指令
            return
        probability = random.randint(0, 101)
        try:
            if (probability < 1) and repeated(self.sender.id, self.app.account, 2):
                await self.app.send_group_message(self.sender, self.message.as_sendable())
                save(
                    self.sender.id,
                    self.app.account,
                    self.message.as_persistent_string(),
                )
                logger.info(f"Random Repeat: {self.message.display}")
            if repeated(self.sender.id, self.app.account, 2):
                await self.app.send_group_message(self.sender, self.message.as_sendable())
                save(
                    self.sender.id,
                    self.app.account,
                    self.message.as_persistent_string(),
                )
                logger.info(f"Follow Repeat: {self.message.display}")
        except Exception as e:
            logger.warning(e)
