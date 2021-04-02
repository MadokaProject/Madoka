from functools import wraps


def permission_required(level='ADMIN'):
    def decorator(func):
        @wraps(func)
        async def with_wrapper(*args, **kwargs):
            if args[0].check_admin():
                return await func(*args, **kwargs)
            else:
                args[0].not_admin()

        return with_wrapper

    return decorator
