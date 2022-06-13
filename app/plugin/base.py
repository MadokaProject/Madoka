from typing import List

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, Image
from graia.ariadne.model import Friend, Group, Member
from graia.broadcast.interrupt import InterruptControl

from app.core.commander import CommandDelegateManager
from app.util.control import Permission
from app.util.permission import *
from app.util.text2image import create_image
from app.util.tools import parse_args


class Plugin:
    """存储消息"""

    def __init__(self, *args):
        for arg in args:
            if isinstance(arg, MessageChain):
                self.message = arg  # 消息内容
                self.msg: List[str] = parse_args(self.message.asDisplay())
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
            elif isinstance(arg, Config):
                self.config = arg

    def get_qid(self):
        """获取发言人QQ号"""
        if hasattr(self, 'group'):
            return self.member.id
        elif hasattr(self, 'friend'):
            return self.friend.id

    @classmethod
    async def print_help(cls, help_doc: str):
        return MessageChain.create([Image(data_bytes=await create_image(help_doc, 80))])

    @classmethod
    def unkown_error(cls):
        """未知错误默认回复消息"""
        return MessageChain.create([Plain(
            '未知错误，请联系管理员处理！'
        )])

    @classmethod
    def args_error(cls):
        """参数错误默认回复消息"""
        return MessageChain.create([Plain(
            '输入的参数错误！'
        )])

    @classmethod
    def index_error(cls):
        """索引错误默认回复消息"""
        return MessageChain.create([Plain(
            '索引超出范围！'
        )])

    @classmethod
    def arg_type_error(cls):
        """类型错误默认回复消息"""
        return MessageChain.create([Plain(
            '参数类型错误！'
        )])

    @classmethod
    def exec_permission_error(cls):
        """权限不够回复消息"""
        return MessageChain.create([Plain(
            '没有相应操作权限！'
        )])

    @classmethod
    def point_not_enough(cls):
        return MessageChain.create([Plain(
            f'你的{Config().COIN_NAME}不足哦！'
        )])

    @classmethod
    def not_admin(cls):
        return MessageChain.create([Plain(
            '你的权限不足，无权操作此命令！'
        )])

    @classmethod
    def exec_success(cls):
        return MessageChain.create([Plain(
            '指令执行成功！'
        )])

    def check_admin(self, level: int):
        """检查是否管理员"""
        if Permission.require(self.member if hasattr(self, 'group') else self.friend, level):
            return True
        return False
