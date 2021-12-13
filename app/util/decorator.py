from functools import wraps
from app.util.control import Permission


def permission_required(level: int = None):
    def decorator(func):
        @wraps(func)
        async def with_wrapper(*args, **kwargs):
            if level:
                if Permission.get(args[0].member if hasattr(args[0], 'group') else args[0].friend.id) >= level:
                    return await func(*args, **kwargs)
                else:
                    args[0].not_admin()
            elif args[0].check_admin():
                return await func(*args, **kwargs)
            else:
                args[0].not_admin()

        return with_wrapper

    return decorator
