from loguru import logger

from app.core.config import Config
from app.trigger.trigger import Trigger
from app.util.control import Permission
from app.util.graia import message


class ChangeMode(Trigger):
    async def process(self):
        msg = self.message.display
        if msg[0] in Config.command.headers and msg[1:] == "mode":
            await self.change_mode(self.target, self.sender)
        if Config.online and Config.debug:
            self.as_last = True

    @Permission.require(level=Permission.MASTER)
    async def change_mode(self, _, sender):
        if Config.online:
            if Config.debug:
                message(">> 已退出DEBUG模式！\r\n>> 服务端进入工作状态！").target(sender).send()
                logger.info(">> 已退出DEBUG模式！  >> 服务端进入工作状态！")
            else:
                message(">> 已进入DEBUG模式！\r\n>> 服务端进入休眠状态！").target(sender).send()
                logger.info(">> 已进入DEBUG模式！  >> 服务端进入休眠状态！")
        Config.change_debug()
        self.as_last = True
