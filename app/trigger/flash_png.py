from datetime import datetime

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import FlashImage, Plain, Forward, ForwardNode
from graia.ariadne.model import Friend, Group

from app.core.settings import config
from app.trigger.trigger import Trigger
from app.util.online_config import get_config


class FlashPng(Trigger):
    async def process(self):
        if self.message.has(FlashImage):
            message = MessageChain(Forward([
                ForwardNode(
                    target=self.target,
                    time=datetime.now(),
                    message=MessageChain(Plain('识别到闪照如下')),
                ),
                ForwardNode(
                    target=self.target,
                    time=datetime.now(),
                    message=MessageChain(self.message.get_first(FlashImage).to_image())
                )
            ]))
            if isinstance(self.sender, Friend):
                await self.app.send_friend_message(config.MASTER_QQ, message)
            elif isinstance(self.sender, Group) and await get_config('flash_png', self.sender.id):
                await self.do_send(message)
