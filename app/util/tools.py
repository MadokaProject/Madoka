import asyncio
import os
import sys
from pathlib import Path
from typing import List, Union


def parse_args(args, keep_head=False) -> list:
    """拆分指令参数为一个列表，并去除入口指令
    :param args: str 字符串
    :param keep_head: bool 保留头部
    """
    args: List[str] = args.strip().split()
    for arg in args:
        arg.strip()
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
    return any(full_match and prefix == arg or not full_match and prefix.startswith(arg) for arg in args)


def restart(*args):
    python = sys.executable
    os.execl(python, python, *[sys.argv[0], *args])


def app_path(*join_paths) -> Path:
    """获取 app 绝对路径"""
    return Path(__file__).parent.parent.joinpath(*join_paths)


async def to_thread(func, /, *args, **kwargs):
    """3.9后新增的方法"""
    return await asyncio.to_thread(func, *args, **kwargs)


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
