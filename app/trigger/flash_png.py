from datetime import datetime

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import FlashImage, Plain, Forward, ForwardNode

from app.core.config import Config
from app.trigger.trigger import Trigger
from app.util.online_config import get_config


class FlashPng(Trigger):
    async def process(self):
        if self.message.has(FlashImage):
            user = self.member if hasattr(self, 'group') else self.friend
            message = MessageChain(Forward([
                ForwardNode(
                    target=user,
                    time=datetime.now(),
                    message=MessageChain(Plain('识别到闪照如下')),
                ),
                ForwardNode(
                    target=user,
                    time=datetime.now(),
                    message=MessageChain(self.message.get_first(FlashImage).to_image())
                )
            ]))
            if hasattr(self, 'friend'):
                await self.app.send_friend_message(Config().MASTER_QQ, message)
            elif hasattr(self, 'group') and await get_config('flash_png', self.group.id):
                await self.do_send(message)
