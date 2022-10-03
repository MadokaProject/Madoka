from loguru import logger

from app.core.settings import config
from app.trigger.trigger import Trigger
from app.util.control import Permission
from app.util.graia import message


class ChangeMode(Trigger):
    async def process(self):
        if self.message.display == ".mode":
            await self.change_mode(self.target, self.sender)
        if config.ONLINE and config.DEBUG:
            self.as_last = True

    @Permission.require(level=Permission.MASTER)
    async def change_mode(self, _, sender):
        if config.ONLINE:
            if config.DEBUG:
                message(">> 已退出DEBUG模式！\r\n>> 服务端进入工作状态！").target(sender).send()
                logger.info(">> 已退出DEBUG模式！  >> 服务端进入工作状态！")
            else:
                message(">> 已进入DEBUG模式！\r\n>> 服务端进入休眠状态！").target(sender).send()
                logger.info(">> 已进入DEBUG模式！  >> 服务端进入休眠状态！")
        config.change_debug()
        self.as_last = True
