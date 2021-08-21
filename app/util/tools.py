import os
import sys
from typing import List
from graia.application.group import MemberPerm


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


def app_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def message_source(self) -> bool:
    """判断消息来源

    :return: bool 群消息: True, 好友消息: False
    """
    try:
        if self.friend.id:
            return False
    except:
        return True


def check_bot_permit(self) -> bool:
    """验证机器人管理权限

    :return: bool 管理权限: True, 普通权限: False
    """
    if self.group.accountPerm == MemberPerm.Member:
        return False
    else:
        return True
