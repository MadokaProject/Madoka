from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.message.parser.twilight import MatchResult

from app.util.tools import *


class ConsoleController:
    def __init__(self, *args):
        for arg in args:
            if isinstance(arg, MatchResult):
                self.param: List[str] = parse_args(arg.result.asDisplay())  # 命令内容
            elif isinstance(arg, Console):
                self.console = arg
            elif isinstance(arg, Ariadne):
                self.app = arg
        self.resp = None

    @staticmethod
    def unkown_error(msg=None):
        """未知错误默认回复消息"""
        return '未知错误\n' + msg or ''

    @staticmethod
    def args_error(msg=None):
        """参数错误默认回复消息"""
        return msg or '输入的参数错误！'

    @staticmethod
    def arg_type_error():
        """类型错误默认回复消息"""
        return '参数类型错误！'

    @staticmethod
    def exec_permission_error():
        """权限不够回复消息"""
        return '没有相应操作权限！'

    @staticmethod
    def exec_success():
        return '指令执行成功！'
