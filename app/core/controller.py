import sys

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image

from app.core.settings import *
from app.plugin.base import Plugin
from app.trigger import *
from app.util.control import Permission
from app.util.permission import check_permit
from app.util.text2image import create_image
from app.util.tools import isstartswith, Autonomy


class Controller:
    def __init__(self, *args):
        """存储消息"""
        self.args = Plugin(*args)

    async def process_event(self):
        msg = self.args.message.display
        send_help = False  # 是否为主菜单帮助
        resp = None
        i = 1

        # 判断是否在权限允许列表
        if hasattr(self.args, 'friend'):
            if self.args.friend.id not in ACTIVE_USER:
                return
        elif hasattr(self, 'group'):
            if self.args.group.id not in ACTIVE_GROUP:
                return

        # 自定义预触发器
        for trig in trigger.Trigger.__subclasses__():
            obj: trigger.Trigger
            if hasattr(self.args, 'friend'):
                obj = trig(self.args.message, self.args.friend, self.args.app)
            elif hasattr(self.args, 'group'):
                obj = trig(self.args.message, self.args.group, self.args.member, self.args.app)
            else:
                continue
            if not obj.enable:
                continue
            await obj.process()
            if obj.as_last:
                break
        if self.args.config.ONLINE and self.args.config.DEBUG:
            return

        # 判断是否为黑名单用户
        if (getattr(self.args, 'friend', None) or getattr(self.args, 'member', None)).id in BANNED_USER:
            return

        if msg[0] not in self.args.manager.headers:  # 判断是否为指令
            return

        # 指令规范化
        if not msg[0] == '.':
            msg = '.' + msg[1:]

        # 判断是否为主菜单帮助
        if isstartswith(msg, ['.help', '.帮助']):
            send_help = True
            if hasattr(self.args, 'group'):
                resp = (
                        f"{self.args.config.BOT_NAME} 群菜单 / {self.args.group.id}\n{self.args.group.name}\n"
                        + "========================================================"
                )
            else:
                resp = (
                        f"{self.args.config.BOT_NAME} 好友菜单 / {self.args.friend.id}\n{self.args.friend.nickname}\n"
                        + "========================================================"
                )

        # 加载插件
        for plg in self.args.manager.get_delegates().copy().values():
            enable = plg.enable
            hidden = plg.hidden
            if hasattr(self.args, 'friend'):
                if not check_permit(self.args.friend.id, 'friend', plg.entry):
                    enable = False
            elif hasattr(self.args, 'group'):
                if not check_permit(self.args.group.id, 'group', plg.entry):
                    enable = False
            if Permission.require(self.args.member if hasattr(self.args, 'group') else self.args.friend,
                                  Permission.SUPER_ADMIN):
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
            elif isstartswith(msg.split()[0][1:], plg.entry, full_match=1):
                if enable:
                    current = sys.stdout
                    alc_help = Autonomy()
                    sys.stdout = alc_help
                    try:
                        result = plg.alc.parse(self.args.message)
                        if result.matched:
                            sys.stdout = current
                            resp = await plg.func(self.args, result, plg.alc)
                        elif result.head_matched:
                            if alc_help.buff:
                                resp = MessageChain([Image(data_bytes=await create_image(alc_help.buff, 80))])
                            else:
                                resp = MessageChain(Plain('参数错误!'))
                            sys.stdout = current
                    except Exception as e:
                        resp = MessageChain(Plain(f'{e}'))
                    sys.stdout = current
                else:
                    resp = MessageChain([Plain('此功能未开启！')])
                await self._do_send(resp)

        # 主菜单帮助发送
        if send_help:
            resp += (
                    "\n========================================================"
                    + "\n详细功能帮助菜单请发送 .<功能> --help, -h, 例如: .gp --help"
                    + "\n管理员可通过插件管理工具开关功能"
                    + "\n所有功能均需添加前缀 ."
                    + "\n源码: github.com/MadokaProject/Madoka"
            )
            await self._do_send(MessageChain([Image(data_bytes=await create_image(resp, 80))]))

    async def _do_send(self, resp):
        """发送消息"""
        if not isinstance(resp, MessageChain):
            return
        if hasattr(self.args, 'friend'):  # 发送好友消息
            await self.args.app.send_friend_message(self.args.friend, resp)
        elif hasattr(self.args, 'group'):  # 发送群聊消息
            await self.args.app.send_group_message(self.args.group, resp)
