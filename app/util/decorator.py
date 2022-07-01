import inspect
from functools import wraps
from typing import Callable

from graia.ariadne.model import Friend, Member

from app.plugin.base import not_admin
from app.util.control import Permission


class ArgsAssigner:
    """参数分配器"""

    def __init__(self, func: Callable):
        self.func = func
        self.signature = inspect.signature(self.func)

    def __call__(self, *args, **kwargs):
        self.args = []
        for i in self.signature.parameters.values():
            if str(i.kind) in ('POSITIONAL_OR_KEYWORD', 'KEYWORD_ONLY'):
                for arg in args:
                    _type = i.annotation
                    if hasattr(i.annotation, '__args__'):
                        _type = i.annotation.__args__
                    if isinstance(arg, _type):
                        self.args.append(arg)
                        break
                else:
                    if isinstance(i.default, type) and i.default.__name__ == '_empty':
                        self.args.append(None)
                    else:
                        self.args.append(i.default)
        return self.func(*self.args, **kwargs)


def permission_required(level: int = Permission.GROUP_ADMIN):
    """插件鉴权

    :param level: 允许的权限
    """

    def decorator(func):
        @wraps(func)
        async def with_wrapper(*args, **kwargs):
            for arg in args:
                if isinstance(arg, Friend) or isinstance(arg, Member):
                    target = arg
                    break
            else:
                raise TypeError("被装饰函数必须包含一个 Friend 或 Member 参数")
            if Permission.require(target, level):
                return await func(*args, **kwargs)
            else:
                return not_admin()

        return with_wrapper

    return decorator
