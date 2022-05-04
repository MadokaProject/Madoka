import asyncio
import contextvars
import functools
import os
import sys
from typing import List, Union


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


def isstartswith(prefix: str, args: Union[str, list], full_match=False) -> bool:
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


def restart(*args):
    python = sys.executable
    os.execl(python, python, *[sys.argv[0], *args])


def app_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def to_thread(func, /, *args, **kwargs):
    """3.9后新增的方法"""
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


class Autonomy:
    """重定向输出到变量"""

    def __init__(self):
        self._buff = ""

    def write(self, out_stream):
        """
        :param out_stream:
        :return:str
        """
        self._buff += out_stream

    @property
    def buff(self):
        return self._buff
