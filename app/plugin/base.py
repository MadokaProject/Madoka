from graia.application import MessageChain, GraiaMiraiApplication, Friend, Group, Member
from graia.application.message.elements.internal import Plain

from app.util.permission import *
from app.util.tools import *


class Plugin:
    """插件继承此父类，并重写下面三个参数
    :param entry: 程序入口点参数
    :param brief_help: 简短帮助，显示在主帮助菜单
    :param full_help: 完整帮助，显示在插件帮助菜单
    """
    entry = ['.plugin']
    brief_help = entry[0] + 'this is a brief help.'
    full_help = 'this is a detail help.'
    enable = True
    hidden = False

    def __init__(self, message, *args):
        """根据需求可重写此构造方法"""
        self.msg: List[str] = parse_args(message.asDisplay())
        self.message: MessageChain = message
        for arg in args:
            if isinstance(arg, Friend):
                self.friend: Friend = arg  # 消息来源 好友
                if not check_permit(arg.id, 'friend', self.entry[0][1:]):
                    self.enable = False
            elif isinstance(arg, Group):
                self.group: Group = arg  # 消息来源 群聊
                if not check_permit(arg.id, 'group', self.entry[0][1:]):
                    self.enable = False
            elif isinstance(arg, Member):
                self.member: Member = arg  # 群聊消息发送者
            elif isinstance(arg, GraiaMiraiApplication):
                self.app: GraiaMiraiApplication = arg  # 程序执行主体
        self.resp = None

    def _pre_check(self):
        """此方法检查是否为插件帮助指令"""
        if self.msg:
            if isstartswith(self.msg[0], ['help', '帮助']):
                self.resp = MessageChain.create([Plain(
                    self.full_help
                )])

    def print_help(self):
        """回送插件详细帮助"""
        self.resp = MessageChain.create([Plain(
            self.full_help
        )])

    def unkown_error(self):
        """未知错误默认回复消息"""
        self.resp = MessageChain.create([Plain(
            '未知错误，请联系管理员处理！'
        )])

    def args_error(self):
        """参数错误默认回复消息"""
        self.resp = MessageChain.create([Plain(
            '输入的参数错误！'
        )])

    def index_error(self):
        """索引错误默认回复消息"""
        self.resp = MessageChain.create([Plain(
            '索引超出范围！'
        )])

    def arg_type_error(self):
        """类型错误默认回复消息"""
        self.resp = MessageChain.create([Plain(
            '参数类型错误！'
        )])

    def exec_permission_error(self):
        """权限不够回复消息"""
        self.resp = MessageChain.create([Plain(
            '没有相应操作权限！'
        )])

    def point_not_enough(self):
        self.resp = MessageChain.create([Plain(
            '你的积分不足哦！'
        )])

    def not_admin(self):
        self.resp = MessageChain.create([Plain(
            '你不是管理员哦，无权操作此命令！'
        )])

    def exec_success(self):
        self.resp = MessageChain.create([Plain(
            '指令执行成功！'
        )])

    def check_admin(self):
        """检查是否管理员"""
        if hasattr(self, 'group'):
            if self.member.id in ADMIN_USER:
                return True
        elif hasattr(self, 'friend'):
            if self.friend.id in ADMIN_USER:
                return True
        return False

    async def process(self):
        """子类必须重写此方法，此方法用于修改要发送的信息内容"""
        raise NotImplementedError

    async def get_resp(self):
        """程序默认调用的方法以获取要发送的信息"""
        self._pre_check()
        if not self.resp:
            await self.process()
        if self.resp:
            return self.resp
        else:
            return None
