"""
Xenon 管理 https://github.com/McZoo/Xenon/blob/master/lib/control.py
"""
from functools import wraps
from typing import Union

from graia.ariadne.model import Friend, Group, Member, MemberPerm

from app.core.config import Config
from app.core.settings import ADMIN_USER, GROUP_ADMIN_USER, BANNED_USER
from app.util.online_config import set_plugin_switch
from app.util.phrases import not_admin


class Permission:
    """
    用于管理权限的类，不应被实例化
    """

    MASTER = 4
    SUPER_ADMIN = 3
    GROUP_ADMIN = 2
    USER = 1
    BANNED = 0
    DEFAULT = USER
    config: Config = Config()

    @classmethod
    def get(cls, member: Union[Member, Friend, int]) -> int:
        """
        获取用户的权限
        :param member: 用户实例或QQ号
        :return: 等级，整数
        """

        if isinstance(member, Member):
            user = member.id
            user_permission = member.permission
        elif isinstance(member, Friend):
            user = member.id
            user_permission = cls.DEFAULT
        else:
            user = member
            user_permission = cls.DEFAULT

        if user == int(cls.config.MASTER_QQ):
            res = cls.MASTER
        elif user in ADMIN_USER:
            res = cls.SUPER_ADMIN
        elif user in BANNED_USER:
            res = cls.BANNED
        elif user_permission in [MemberPerm.Administrator, MemberPerm.Owner] or user in GROUP_ADMIN_USER:
            res = cls.GROUP_ADMIN
        else:
            res = cls.DEFAULT
        return res

    @classmethod
    def require(cls, level: int = GROUP_ADMIN):
        """
        插件鉴权
        :param level: 允许的权限
        """

        def perm_check(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                for arg in args:
                    if isinstance(arg, Friend) or isinstance(arg, Member):
                        target = arg
                        break
                else:
                    raise TypeError("被装饰函数必须包含一个 Friend 或 Member 参数")
                if cls.manual(target, level):
                    return await func(*args, **kwargs)
                else:
                    return not_admin()

            return wrapper

        return perm_check

    @classmethod
    def manual(cls, member: Union[Member, Friend, int], level: int = DEFAULT) -> bool:
        """
        指示需要 `level` 以上等级才能触发，默认为至少 USER 权限
        :param member: 用户实例或QQ号
        :param level: 限制等级
        """

        if cls.get(member) < level:
            return False
        return True

    @classmethod
    def compare(cls, src: Union[Member, Friend, int], dst: Union[Member, Friend, int]) -> bool:
        """
        比较 src 和 dst 的权限，src大于dst时返回true
        :param src: 比较用户
        :param dst: 被比较用户
        :return: src > dst = True (俩者权限相同时返回False)
        """

        if cls.get(src) > cls.get(dst):
            return True
        return False


class Switch:
    """用于开关功能的类，不应被实例化"""

    @classmethod
    async def plugin(cls, src: Union[Member, Friend, int], perm, dst: Union[Group, int]):
        if isinstance(src, Member):
            if not Permission.manual(src, Permission.GROUP_ADMIN):
                return '你的权限不足，无权操作此命令'
        else:
            if not Permission.manual(src, Permission.SUPER_ADMIN) and not Permission.compare(src, dst):
                return '你的权限不足，无权操作此命令'
        if await set_plugin_switch(dst, perm):
            return '操作成功'
        else:
            return '操作失败'
