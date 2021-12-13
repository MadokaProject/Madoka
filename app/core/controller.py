from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from graia.ariadne.model import Friend, Group, Member
from graia.broadcast.interrupt import InterruptControl

from app.core.config import Config
from app.core.settings import *
from app.trigger import *
from app.util.control import Permission
from app.util.tools import isstartswith


class Controller:
    def __init__(self, plugin: list, *args):
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
            elif isinstance(arg, Ariadne):
                self.app = arg  # 程序执行主体

    async def process_event(self):
        msg = self.message.asDisplay()
        send_help = False  # 是否为主菜单帮助
        resp = '[√]\t帮助：help'

        # 判断是否在权限允许列表
        if hasattr(self, 'friend'):
            if self.friend.id not in ACTIVE_USER or self.friend.id in BANNED_USER:
                return
        elif hasattr(self, 'group'):
            if self.group.id not in ACTIVE_GROUP or self.member.id in BANNED_USER:
                return

        # 自定义预触发器
        for trig in trigger.Trigger.__subclasses__():
            obj = None
            if hasattr(self, 'friend'):
                obj = trig(self.message, self.friend, self.app)
            elif hasattr(self, 'group'):
                obj = trig(self.message, self.group, self.member, self.app)
            if not obj.enable:
                continue
            await obj.process()
            if obj.as_last:
                break
        config = Config()
        if config.ONLINE and config.DEBUG:
            return

        if msg[0] not in '.,;!?。，；！？/\\':  # 判断是否为指令
            return

        # 指令规范化
        if not msg[0] == '.':
            msg = '.' + msg[1:]

        # 判断是否为主菜单帮助
        if isstartswith(msg, ['.help', '.帮助']):
            send_help = True

        # 加载插件
        for plugin in self.plugin:
            obj = None
            if hasattr(self, 'friend'):
                obj = plugin.Module(self.message, self.friend, self.app)
            elif hasattr(self, 'group'):
                obj = plugin.Module(self.message, self.group, self.member, self.source, self.inc, self.app)
            if (hasattr(self, 'group') and Permission.get(self.member) >= Permission.SUPER_ADMIN) or (
                    hasattr(self, 'friend') and Permission.get(self.friend.id) >= Permission.SUPER_ADMIN):
                obj.hidden = False  # 隐藏菜单仅超级管理员以上可见
            if send_help and not obj.hidden:  # 主菜单帮助获取
                if not obj.enable:
                    resp += obj.brief_help.replace('√', '×')
                else:
                    resp += obj.brief_help
            elif isstartswith(msg, obj.entry):  # 指令执行
                resp = await obj.set_switch()
                if obj.enable and not resp:
                    resp = await obj.get_resp()
                elif not resp:
                    resp = MessageChain.create([
                        Plain('此功能未开启！')
                    ])
                await self._do_send(resp)
                break

        # 主菜单帮助发送
        if send_help:
            await self._do_send(MessageChain.create([Plain(resp)]))

    async def _do_send(self, resp):
        """发送消息"""
        if not isinstance(resp, MessageChain):
            return
        if hasattr(self, 'friend'):  # 发送好友消息
            await self.app.sendFriendMessage(self.friend, resp)
        elif hasattr(self, 'group'):  # 发送群聊消息
            await self.app.sendGroupMessage(self.group, resp)
