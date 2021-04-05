import os
import sys
from typing import List


def parse_args(args) -> list:
    """拆分指令参数为一个列表，并去除入口指令
    :param args: str 字符串
    """
    args: List[str] = args.strip().split()
    for i in range(len(args)):
        args[i].strip()
    args.pop(0)
    return args


def isstartswith(prefix: str, args) -> bool:
    """判断prefix是否以args中某元素开头"""
    if type(args) == str:
        args = [args]
    for arg in args:
        if prefix.startswith(arg):
            return True
    return False


def restart(*args):
    python = sys.executable
    os.execl(python, python, *[sys.argv[0], *args])
