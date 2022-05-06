import sys
from types import ModuleType
from typing import List

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, Image
from graia.ariadne.model import Friend, Group, Member
from graia.broadcast.interrupt import InterruptControl

from app.core.Exceptions import NonStandardPlugin
from app.core.commander import CommandDelegateManager
from app.core.settings import *
from app.plugin.base import Plugin
from app.trigger import *
from app.util.control import Permission
from app.util.text2image import create_image
from app.util.tools import isstartswith, Autonomy


class Controller:
    def __init__(self, plugin: List[ModuleType], *args):
        """存储消息"""
        self.plugin = plugin  # 插件列表
        for arg in args:
            if isinstance(arg, MessageChain):
                self.message = arg  # 消息内容
            elif isinstance(arg, Friend):
                self.friend = arg  # 消息来源 好友
            elif isinstance(arg, Group):
                self.group = arg  # 消息来源 群聊
            elif isinstance(arg, Member):
                self.member = arg  # 群聊消息发送者
            elif isinstance(arg, Source):
                self.source = arg  # 消息标识
            elif isinstance(arg, InterruptControl):
                self.inc = arg  # 中断器
            elif isinstance(arg, CommandDelegateManager):
                self.manager = arg
            elif isinstance(arg, Ariadne):
                self.app = arg  # 程序执行主体

    async def process_event(self):
        msg = self.message.asDisplay()
        send_help = False  # 是否为主菜单帮助
        resp = None
        i = 1

        # 判断是否在权限允许列表
        if hasattr(self, 'friend'):
            if self.friend.id not in ACTIVE_USER:
                return
        elif hasattr(self, 'group'):
            if self.group.id not in ACTIVE_GROUP:
                return

        # 自定义预触发器
        for trig in trigger.Trigger.__subclasses__():
            obj: trigger.Trigger
            if hasattr(self, 'friend'):
                obj = trig(self.message, self.friend, self.app)
            elif hasattr(self, 'group'):
                obj = trig(self.message, self.group, self.member, self.app)
            else:
                continue
            if not obj.enable:
                continue
            await obj.process()
            if obj.as_last:
                break
        config = Config()
        if config.ONLINE and config.DEBUG:
            return

        # 判断是否为黑名单用户
        if (getattr(self, 'friend', None) or getattr(self, 'member', None)).id in BANNED_USER:
            return

        if msg[0] not in self.manager.headers:  # 判断是否为指令
            return

        # 指令规范化
        if not msg[0] == '.':
            msg = '.' + msg[1:]

        # 判断是否为主菜单帮助
        if isstartswith(msg, ['.help', '.帮助']):
            send_help = True
            if hasattr(self, 'group'):
                resp = (
                        f"{config.BOT_NAME} 群菜单 / {self.group.id}\n{self.group.name}\n"
                        + "========================================================"
                )
            else:
                resp = (
                        f"{config.BOT_NAME} 好友菜单 / {self.friend.id}\n{self.friend.nickname}\n"
                        + "========================================================"
                )

        # 加载插件
        for plugin in self.plugin:
            plg: Plugin
            if not hasattr(plugin, 'Module'):
                raise NonStandardPlugin(plugin.__name__)
            if hasattr(self, 'friend'):
                plg = plugin.Module(self.message, self.friend, self.inc, self.app)
            elif hasattr(self, 'group'):
                plg = plugin.Module(self.message, self.group, self.member, self.source, self.inc, self.app)
            else:
                continue
            if Permission.require(self.member if hasattr(self, 'group') else self.friend, Permission.SUPER_ADMIN):
                plg.hidden = False  # 隐藏菜单仅超级管理员以上可见
            if send_help and not plg.hidden:  # 主菜单帮助获取
                if not plg.enable:
                    statu = "【  关闭  】"
                else:
                    statu = "            "
                if i < 10:
                    si = " " + str(i)
                else:
                    si = str(i)
                resp += f"\n{si}  {statu}  {plg.brief_help}: {plg.entry}"
                i += 1
            elif isstartswith(msg.split()[0][1:], plg.entry, full_match=1):  # 指令执行
                if plg.enable:
                    namespace = plg.__module__.split('.')
                    alc_s = self.manager.get_commands(f'{namespace[-3]}_{namespace[-2]}')
                    current = sys.stdout
                    alc_help = Autonomy()
                    sys.stdout = alc_help
                    for alc in alc_s:
                        if not (call := self.manager.get_delegate(alc.path)):
                            continue
                        try:
                            result = alc.parse(self.message)
                            if result.matched:
                                sys.stdout = current
                                resp = await getattr(plg, call.__name__)(result, alc)
                                break
                            elif result.head_matched:
                                if alc_help.buff:
                                    resp = MessageChain.create([Image(data_bytes=await create_image(alc_help.buff, 80))])
                                else:
                                    resp = MessageChain.create(Plain('参数错误!'))
                                sys.stdout = current
                                break
                        except Exception as e:
                            resp = MessageChain.create(Plain(f'{e}'))
                    sys.stdout = current
                else:
                    resp = MessageChain.create([Plain('此功能未开启！')])
                await self._do_send(resp)
                break

        # 主菜单帮助发送
        if send_help:
            resp += (
                    "\n========================================================"
                    + "\n详细功能帮助菜单请发送 .<功能> --help, -h, 例如: .gp --help"
                    + "\n管理员可通过插件管理工具开关功能"
                    + "\n所有功能均需添加前缀 ."
                    + "\n源码: github.com/MadokaProject/Madoka"
            )
            await self._do_send(MessageChain.create([Image(data_bytes=await create_image(resp, 80))]))

    async def _do_send(self, resp):
        """发送消息"""
        if not isinstance(resp, MessageChain):
            return
        if hasattr(self, 'friend'):  # 发送好友消息
            await self.app.sendFriendMessage(self.friend, resp)
        elif hasattr(self, 'group'):  # 发送群聊消息
            await self.app.sendGroupMessage(self.group, resp)
