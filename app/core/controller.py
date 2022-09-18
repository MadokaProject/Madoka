import sys
from typing import Union

from graia.ariadne import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, Source
from graia.ariadne.model import Friend, Group, Member
from graia.broadcast.interrupt import InterruptControl

from app.core.commander import CommandDelegateManager
from app.core.settings import ACTIVE_GROUP, ACTIVE_USER, BANNED_USER, config
from app.trigger import trigger
from app.util.control import Permission
from app.util.decorator import ArgsAssigner
from app.util.permission import check_permit
from app.util.text2image import create_image
from app.util.tools import Autonomy, isstartswith


@ArgsAssigner
class Controller:
    def __init__(
        self,
        app: Ariadne,
        message: MessageChain,
        target: Union[Friend, Member],
        sender: Union[Friend, Group],
        source: Source,
        inc: InterruptControl,
        manager: CommandDelegateManager,
    ):
        """存储消息"""
        self.app = app
        self.message = message
        self.target = target
        self.sender = sender
        self.source = source
        self.inc = inc
        self.manager = manager

    async def process_event(self):
        msg = self.message.display
        send_help = False  # 是否为主菜单帮助
        resp = None
        i = 1

        # 判断是否在权限允许列表
        if isinstance(self.sender, Friend):
            if self.sender.id not in ACTIVE_USER:
                return
        elif isinstance(self.sender, Group):
            if self.sender.id not in ACTIVE_GROUP:
                return

        # 预触发器
        for trig in trigger.Trigger.__subclasses__():
            obj: trigger.Trigger
            obj = trig(self.app, self.target, self.sender, self.source, self.message)
            if not obj.enable:
                continue
            await obj.process()
            if obj.as_last:
                break
        if config.ONLINE and config.DEBUG:
            return

        # 判断是否为黑名单用户
        if self.target.id in BANNED_USER:
            return

        if msg[0] not in self.manager.headers:  # 判断是否为指令
            return

        # 指令规范化
        if not msg[0] == ".":
            msg = "." + msg[1:]

        # 判断是否为主菜单帮助
        if isstartswith(msg, [".help", ".帮助"]):
            send_help = True
            if isinstance(self.sender, Group):
                resp = (
                    f"{config.BOT_NAME} 群菜单 / {self.sender.id}\n{self.sender.name}\n"
                    + "========================================================"
                )
            else:
                resp = (
                    f"{config.BOT_NAME} 好友菜单 / {self.sender.id}\n{self.sender.nickname}\n"
                    + "========================================================"
                )

        # 加载插件
        for plg in self.manager.get_delegates().copy().values():
            enable = plg.enable
            hidden = plg.hidden
            if not check_permit(self.sender, plg.entry):
                enable = False
            if Permission.manual(self.target, Permission.SUPER_ADMIN):
                hidden = False  # 隐藏菜单仅超级管理员以上可见
            if send_help and not hidden:  # 主菜单帮助获取
                if not enable:
                    statu = "【  关闭  】"
                else:
                    statu = "            "
                if i < 10:
                    si = " " + str(i)
                else:
                    si = str(i)
                resp += f"\n{si}  {statu}  {plg.brief_help}: {plg.entry}"
                i += 1
            elif isstartswith(msg.split()[0][1:], plg.entry, full_match=1) and not hidden:
                if enable:
                    current = sys.stdout
                    alc_help = Autonomy()
                    sys.stdout = alc_help
                    try:
                        result = plg.alc.parse(self.message)
                        if result.matched:
                            sys.stdout = current
                            resp = await plg.func(
                                self.app,
                                self.message,
                                self.target,
                                self.sender,
                                self.source,
                                self.inc,
                                result,
                                plg.alc,
                            )
                        elif result.head_matched:
                            if alc_help.buff:
                                resp = MessageChain([Image(data_bytes=await create_image(alc_help.buff, 80))])
                            else:
                                plg.alc.parse(self.message.extend(["-cp"]))
                                resp = alc_help.buff
                                if not resp:
                                    resp = "参数错误!"
                                resp = MessageChain(resp)
                    except Exception as e:
                        resp = MessageChain(Plain(f"{e}"))
                    finally:
                        sys.stdout = current
                else:
                    resp = MessageChain([Plain("此功能未开启！")])
                await self._do_send(resp)

        # 主菜单帮助发送
        if send_help:
            resp += (
                "\n========================================================"
                + "\n详细功能帮助菜单请发送 .<功能> --help, -h, 例如: .gp --help"
                + "\n管理员可通过插件管理工具开关功能"
                + f"\n所有功能均需添加前缀 {' '.join(i for i in config.COMMAND_HEADERS)}"
                + "\n源码: github.com/MadokaProject/Madoka"
            )
            await self._do_send(MessageChain([Image(data_bytes=await create_image(resp, 80))]))

    async def _do_send(self, resp):
        """发送消息"""
        if not isinstance(resp, MessageChain):
            return
        await self.app.send_message(self.sender, resp)
