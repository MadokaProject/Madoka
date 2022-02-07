from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import FlashImage, Plain

from app.core.config import Config
from app.trigger.trigger import Trigger
from app.util.onlineConfig import get_config


class FlashPng(Trigger):
    async def process(self):
        if self.message.has(FlashImage):
            resp = MessageChain.create([
                    Plain(f'识别到闪照如下：\r\n'),
                    self.message.getFirst(FlashImage).toImage()
                ])
            if hasattr(self, 'friend'):
                await self.app.sendFriendMessage(Config().MASTER_QQ, resp.extend(MessageChain.create([
                    Plain(f'来自{self.friend.nickname}:{self.friend.id}')
                ])))
            elif hasattr(self, 'group') and await get_config('flash_png', self.group.id):
                await self.do_send(resp)
