from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.settings import config
from app.trigger.trigger import Trigger
from app.util.control import Permission


class ChangeMode(Trigger):
    async def process(self):
        if self.message.display == ".mode":
            await self.change_mode(self.target)
        if config.ONLINE and config.DEBUG:
            self.as_last = True

    @Permission.require(level=Permission.MASTER)
    async def change_mode(self, _):
        if config.ONLINE:
            if config.DEBUG:
                await self.do_send(MessageChain([Plain(">> 已退出DEBUG模式！\r\n>> 服务端进入工作状态！")]))
                logger.info(">> 已退出DEBUG模式！  >> 服务端进入工作状态！")
            else:
                await self.do_send(MessageChain([Plain(">> 已进入DEBUG模式！\r\n>> 服务端进入休眠状态！")]))
                logger.info(">> 已进入DEBUG模式！  >> 服务端进入休眠状态！")
        config.change_debug()
        self.as_last = True
