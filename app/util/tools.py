import asyncio
import contextvars
import functools
import os
import sys
from typing import List, Dict, Union


def parse_args(args, keep_head=False) -> list:
    """拆分指令参数为一个列表，并去除入口指令
    :param args: str 字符串
    :param keep_head: bool 保留头部
    """
    args: List[str] = args.strip().split()
    for i in range(len(args)):
        args[i].strip()
    if not keep_head:
        args.pop(0)
    return args


def isstartswith(prefix: str, args, full_match=False) -> bool:
    """判断prefix是否以args中某元素开头
    :param prefix: 被匹配元素
    :param args: 匹配元素
    :param full_match: 完全匹配
    """
    if type(args) == str:
        args = [args]
    for arg in args:
        if full_match:
            if prefix == arg:
                return True
        elif prefix.startswith(arg):
            return True
    return False


def command_help_parse(commands: Dict[str, Union[str, Dict]], tier=1) -> str:
    """命令菜单解析器

    :param commands: Dict结构命令菜单
    :param tier: 当前命令层级(该参数一般无需填写)
    """
    commands_help = ''
    for command, desc in commands.items():
        for i in range(tier):
            commands_help += '\t'
        if isinstance(desc, str):
            commands_help += f"{format(command, '<30')}{desc}\n"
        elif isinstance(desc, Dict):
            commands_help += f"{format(command, '<30')}{command_help_parse(desc, tier+1)}"
    return commands_help


def command_parse(commands: List) -> dict:
    """命令解析器

    :param commands: 使用parse_args拆分的指令列表
    """
    result = {}
    flag = False
    for i in range(len(commands)):
        if flag or commands[i][0] == '-':
            if not flag:
                flag = True
                continue
            result.update({commands[i-1]: commands[i]})
            flag = False
        else:
            result.update({commands[i]: command_parse(commands[i+1:])})
            return result
    return result


def restart(*args):
    python = sys.executable
    os.execl(python, python, *[sys.argv[0], *args])


def app_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def to_thread(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)
