from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from graia.ariadne.model import Friend, Group, Member
from graia.broadcast.interrupt import InterruptControl

from app.util.control import Permission
from app.util.permission import *
from app.util.tools import *


class Plugin:
    """插件继承此父类，并重写下面四个参数
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
            elif isinstance(arg, Source):
                self.source: Source = arg  # 消息标识
            elif isinstance(arg, InterruptControl):
                self.inc = arg
            elif isinstance(arg, Ariadne):
                self.app: Ariadne = arg  # 程序执行主体
        self.resp = None

    def get_qid(self):
        """获取发言人QQ号"""
        if hasattr(self, 'group'):
            return self.member.id
        elif hasattr(self, 'friend'):
            return self.friend.id

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
            '你的权限不足，无权操作此命令！'
        )])

    def exec_success(self):
        self.resp = MessageChain.create([Plain(
            '指令执行成功！'
        )])

    def check_admin(self):
        """检查是否管理员"""
        if hasattr(self, 'group'):
            if Permission.get(self.member) >= Permission.GROUP_ADMIN:
                return True
        elif hasattr(self, 'friend'):
            if Permission.get(self.friend.id) >= Permission.SUPER_ADMIN:
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


class Scheduler:
    """计划任务继承此父类，并重写下面一个参数。该类用于插件开发者设置计划任务
    :param cron: cron 表达式
    """
    cron = False

    def __init__(self, app):
        self.app: Ariadne = app

    async def process(self):
        """子类必须重写此方法，此方法用于执行计划任务"""
        raise NotImplementedError


class InitDB:
    """初始化数据表继承此父类。该类用于插件开发者创建所需数据表
    （注意：数据表命名格式：Plugin_<插件名>_<表名>，如: Plugin_base_demo）
    """

    async def process(self):
        """子类必须重写此方法，此方法用于创建所需数据表"""
        raise NotImplementedError
