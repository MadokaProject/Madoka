from graia.application import GraiaMiraiApplication
from graia.application.friend import Friend
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image

from app.core.settings import *
from app.event.reply import Reply, Repeat
from app.plugin import *
from app.plugin.chat import Chat
from app.util.csm import csm
from app.util.msg import save
from app.util.tools import isstartswith


class Controller:
    def __init__(self, *args):
        """存储消息"""
        for arg in args:
            if isinstance(arg, MessageChain):
                self.message = arg  # 消息内容
            elif isinstance(arg, Friend):
                self.friend = arg  # 消息来源 好友
            elif isinstance(arg, Group):
                self.group = arg  # 消息来源 群聊
            elif isinstance(arg, Member):
                self.member = arg  # 群聊消息发送者
            elif isinstance(arg, GraiaMiraiApplication):
                self.app = arg  # 程序执行主体

    async def process_event(self):
        msg = self.message.asDisplay()
        send_help = False  # 是否为主菜单帮助
        resp = '▶帮助：help'

        # 判断是否在权限允许列表
        if hasattr(self, 'friend'):
            if self.friend.id not in ACTIVE_USER:
                return
        elif hasattr(self, 'group'):
            if self.group.id not in ACTIVE_GROUP:
                return
            if self.member.id not in ADMIN_USER:
                try:
                    content_record = self.message.get(Plain)[0].dict()['text']
                    type_record = 'text'
                except:
                    content_record = self.message.get(Image)[0].dict()['url']
                    type_record = 'image'
                content_record = msg if type_record == 'text' else content_record
                save(self.group.id, self.member.id, content_record)
                if await csm(self, msg, type_record):
                    return

        if msg[0] not in '.,;!?。，；！？/\\':  # 判断是否为指令
            await Reply(self)
            await Repeat(self)
            await Chat(self)
            return

        # 指令规范化
        if not msg[0] == '.':
            msg = '.' + msg[1:]

        # 判断是否为主菜单帮助
        if isstartswith(msg, ['.help', '.帮助']):
            send_help = True

        # 加载插件
        for plugin in base.Plugin.__subclasses__():
            obj = None
            if hasattr(self, 'friend'):
                obj = plugin(self.message, self.friend, self.app)
            elif hasattr(self, 'group'):
                obj = plugin(self.message, self.group, self.member, self.app)
            if (hasattr(self, 'group') and self.member.id in ACTIVE_USER) or (
                    hasattr(self, 'friend') and self.friend.id in ACTIVE_USER):
                obj.hidden = False
            if send_help and not obj.hidden:  # 主菜单帮助获取
                if not obj.enable:
                    resp += obj.brief_help.replace('√', '×')
                else:
                    resp += obj.brief_help
            elif isstartswith(msg, obj.entry):  # 指令执行
                if obj.enable:
                    resp = await obj.get_resp()
                else:
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
