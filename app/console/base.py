from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.message.parser.twilight import MatchResult

from app.util.tools import *


class ConsoleController:
    """控制台命令继承此父类，并重写下面四个参数
        :param entry: 程序入口点参数
        :param brief_help: 简短帮助，显示在主帮助菜单
        :param full_help: 完整帮助，显示在命令帮助菜单
        """
    entry: str = '.plugin'
    brief_help: str = 'this is a brief help.'
    full_help: Dict[str, str] = {
        'command': 'this is a detail help.'
    }

    def __init__(self, *args):
        for arg in args:
            if isinstance(arg, MatchResult):
                self.param: List[str] = parse_args(arg.result.asDisplay())  # 命令内容
            elif isinstance(arg, Console):
                self.console = arg
            elif isinstance(arg, Ariadne):
                self.app = arg
        self.resp = None

    def _pre_check(self):
        """检查是否为帮助菜单指令"""
        if self.param:
            if isstartswith(self.param[0], ['-h', '--help']):
                self.print_help()
            elif isstartswith(self.param[-1], ['-h', '--help']):
                full_help = self.full_help
                usage = self.entry
                try:
                    for i in self.param[:-1]:
                        full_help = full_help[i]
                        usage += f' {i}'
                    usage += ' [OPTION]'
                    self.print_help(full_help, usage)
                except KeyError:
                    self.args_error()

    def print_help(self, full_help=None, usage=None):
        """回送详细帮助

        :param full_help: 自定义菜单，一般用于子菜单帮助回送
        :param usage: 自定义 Usage, 一般用于子菜单帮助回送
        """
        if not full_help:
            full_help = self.full_help
        if not usage:
            usage = f"{format(f'{self.entry} [OPTION]', '<30')}{self.brief_help}\n"
        full_help.update({'-h, --help': '获取帮助菜单'})
        self.resp = f"Usage: {usage}{command_help_parse(full_help)}"

    def unkown_error(self, msg=None):
        """未知错误默认回复消息"""
        self.resp = '未知错误，请联系管理员处理！\n' + msg or ''

    def args_error(self, msg=None):
        """参数错误默认回复消息"""
        self.resp = msg or '输入的参数错误！'

    def arg_type_error(self):
        """类型错误默认回复消息"""
        self.resp = '参数类型错误！'

    def exec_permission_error(self):
        """权限不够回复消息"""
        self.resp = '没有相应操作权限！'

    def exec_success(self):
        self.resp = '指令执行成功！'

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
