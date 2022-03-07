from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image, Source
from graia.ariadne.model import Friend, Group, Member
from graia.broadcast.interrupt import InterruptControl

from app.util.control import Permission
from app.util.permission import *
from app.util.text2image import create_image
from app.util.tools import *


class Plugin:
    """插件继承此父类，并重写下面四个参数
    :param entry: 程序入口点参数
    :param brief_help: 简短帮助，显示在主帮助菜单
    """
    entry = 'plugin'
    brief_help = 'this is a brief help.'
    enable = True
    hidden = False

    def __init__(self, message, *args):
        """根据需求可重写此构造方法"""
        self.msg: List[str] = parse_args(message.asDisplay())
        self.message: MessageChain = message
        for arg in args:
            if isinstance(arg, Friend):
                self.friend: Friend = arg  # 消息来源 好友
                if not check_permit(arg.id, 'friend', self.entry):
                    self.enable = False
            elif isinstance(arg, Group):
                self.group: Group = arg  # 消息来源 群聊
                if not check_permit(arg.id, 'group', self.entry):
                    self.enable = False
            elif isinstance(arg, Member):
                self.member: Member = arg  # 群聊消息发送者
            elif isinstance(arg, Source):
                self.source: Source = arg  # 消息标识
            elif isinstance(arg, InterruptControl):
                self.inc = arg
            elif isinstance(arg, Ariadne):
                self.app: Ariadne = arg  # 程序执行主体

    def get_qid(self):
        """获取发言人QQ号"""
        if hasattr(self, 'group'):
            return self.member.id
        elif hasattr(self, 'friend'):
            return self.friend.id

    @staticmethod
    async def print_help(help_doc: str):
        return MessageChain.create([Image(data_bytes=await create_image(help_doc, 80))])

    @staticmethod
    def unkown_error():
        """未知错误默认回复消息"""
        return MessageChain.create([Plain(
            '未知错误，请联系管理员处理！'
        )])

    @staticmethod
    def args_error():
        """参数错误默认回复消息"""
        return MessageChain.create([Plain(
            '输入的参数错误！'
        )])

    @staticmethod
    def index_error():
        """索引错误默认回复消息"""
        return MessageChain.create([Plain(
            '索引超出范围！'
        )])

    @staticmethod
    def arg_type_error():
        """类型错误默认回复消息"""
        return MessageChain.create([Plain(
            '参数类型错误！'
        )])

    @staticmethod
    def exec_permission_error():
        """权限不够回复消息"""
        return MessageChain.create([Plain(
            '没有相应操作权限！'
        )])

    @staticmethod
    def point_not_enough():
        return MessageChain.create([Plain(
            '你的积分不足哦！'
        )])

    @staticmethod
    def not_admin():
        return MessageChain.create([Plain(
            '你的权限不足，无权操作此命令！'
        )])

    @staticmethod
    def exec_success():
        return MessageChain.create([Plain(
            '指令执行成功！'
        )])

    def check_admin(self, level: int):
        """检查是否管理员"""
        if Permission.require(self.member if hasattr(self, 'group') else self.friend, level):
            return True
        return False


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
