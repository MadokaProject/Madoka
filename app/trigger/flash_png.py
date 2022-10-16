from datetime import datetime

from app.core.config import Config
from app.trigger.trigger import Trigger
from app.util.graia import (
    FlashImage,
    Forward,
    ForwardNode,
    Friend,
    Group,
    MessageChain,
    Plain,
    message,
)
from app.util.online_config import get_config


class FlashPng(Trigger):
    async def process(self):
        if self.message.has(FlashImage):
            msg = message(
                Forward(
                    [
                        ForwardNode(
                            target=self.target,
                            time=datetime.now(),
                            message=MessageChain(Plain("识别到闪照如下")),
                        ),
                        ForwardNode(
                            target=self.target,
                            time=datetime.now(),
                            message=MessageChain(self.message.get_first(FlashImage).to_image()),
                        ),
                    ]
                )
            )
            if isinstance(self.sender, Friend):
                msg.target(Config.master_qq).send()
            elif isinstance(self.sender, Group) and await get_config("flash_png", self.sender.id):
                msg.target(self.sender).send()
