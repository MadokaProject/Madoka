import sys
from typing import Union

from loguru import logger

from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.core.settings import ACTIVE_GROUP, ACTIVE_USER, BANNED_USER
from app.trigger.trigger import Trigger
from app.util.control import Permission
from app.util.decorator import ArgsAssigner
from app.util.exceptions.depend import BannedError, NotActivatedError
from app.util.graia import (
    Ariadne,
    Friend,
    Group,
    Image,
    InterruptControl,
    Member,
    MessageChain,
    Source,
    message,
)
from app.util.permission import check_permit
from app.util.text2image import create_image
from app.util.tools import Autonomy, isstartswith


@ArgsAssigner
class Controller:
    def __init__(
        self,
        app: Ariadne,
        _message: MessageChain,
        target: Union[Friend, Member],
        sender: Union[Friend, Group],
        source: Source,
        inc: InterruptControl,
        manager: CommandDelegateManager,
    ):
        """存储消息"""
        self.app = app
        self.message = _message
        self.target = target
        self.sender = sender
        self.source = source
        self.inc = inc
        self.manager = manager

    def is_activate(self):
        """检查是否激活"""
        if any(
            [
                all([isinstance(self.sender, Friend), self.sender.id not in ACTIVE_USER]),
                all([isinstance(self.sender, Group), self.sender.id not in ACTIVE_GROUP]),
            ]
        ):
            raise NotActivatedError(self.sender)

    def is_banned(self):
        """检查是否被禁言"""
        if self.target.id in BANNED_USER:
            raise BannedError(self.target)

    async def trigger(self):
        """预处理"""
        for trig in Trigger.__subclasses__():
            obj: Trigger
            obj = trig(self.app, self.target, self.sender, self.source, self.message)
            if obj.enable:
                await obj.process()
                if obj.as_last:
                    break

    async def process_event(self):
        msg = self.message.display
        send_help = False  # 是否为主菜单帮助
        i = 1

        self.is_activate()
        await self.trigger()

        if Config.online and Config.debug:
            return

        self.is_banned()

        if msg[0] not in Config.command.headers:  # 判断是否为指令
            return

        # 判断是否为主菜单帮助
        if isstartswith(msg[1:], ["help", "帮助"]):
            send_help = True
            _info = ("群菜单", self.sender.name) if isinstance(self.sender, Group) else ("好友菜单", self.sender.nickname)
            resp = [
                f"{Config.name} {_info[0]} / {self.sender.id}\n{_info[1]}\n",
                "========================================================",
            ]

        # 加载插件
        for plg in self.manager.get_delegates().copy().values():
            enable = plg.enable
            hidden = plg.hidden
            if not check_permit(self.sender, plg.entry):
                enable = False
            if Permission.manual(self.target, Permission.SUPER_ADMIN):
                hidden = False  # 隐藏菜单仅超级管理员以上可见
            if hidden:
                continue
            if send_help:  # 主菜单帮助获取
                statu = "            " if enable else "【  关闭  】"
                si = f" {i}" if i < 10 else f"{i}"
                resp.append(f"{si}  {statu}  {plg.brief_help}: {plg.entry}")
                i += 1
            # elif isstartswith(msg.split()[0][1:], plg.entry, full_match=1) and not hidden:
            elif enable:  # 调整插件执行逻辑，完美支持Alconna
                current = sys.stdout
                alc_help = Autonomy()
                sys.stdout = alc_help
                try:
                    result = plg.alc.parse(self.message)
                    if result.matched:
                        sys.stdout = current
                        await plg.func(
                            self.app,
                            self.message,
                            self.target,
                            self.sender,
                            self.source,
                            self.inc,
                            result,
                            plg.alc,
                        )
                        break
                    elif result.head_matched:
                        if alc_help.buff:
                            message([Image(data_bytes=await create_image(alc_help.buff, 80))]).target(
                                self.sender
                            ).send()
                        else:
                            plg.alc.parse(self.message.extend(["-cp"]))
                            resp = alc_help.buff
                            if not resp:
                                resp = "参数错误!"
                            message(resp).target(self.sender).send()
                        break
                except Exception as e:
                    logger.exception(e)
                    message(f"{e}").target(self.sender).send()
                finally:
                    sys.stdout = current

        # 主菜单帮助发送
        if send_help:
            resp.extend(
                [
                    "========================================================",
                    "详细功能帮助菜单请发送 .<功能> --help, -h, 例如: .gp --help",
                    f"所有功能均需添加前缀 {' '.join(Config.command.headers)}",
                    "源码: github.com/MadokaProject/Madoka",
                ]
            )
            message([Image(data_bytes=await create_image("\n".join(resp), 80))]).target(self.sender).send()
