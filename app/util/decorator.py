from functools import wraps

from app.util.control import Permission


def permission_required(level: int = Permission.GROUP_ADMIN):
    """插件鉴权

    :param level: 允许的权限
    """

    def decorator(func):
        @wraps(func)
        async def with_wrapper(*args, **kwargs):
            if Permission.require(args[0].member if hasattr(args[0], 'group') else args[0].friend, level):
                return await func(*args, **kwargs)
            else:
                return args[0].not_admin()

        return with_wrapper

    return decorator
