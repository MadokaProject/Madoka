from functools import wraps
from typing import Callable, List

from loguru import logger

from app.util.decorator import Singleton


class InitDB(metaclass=Singleton):
    _databases: List[Callable]

    def __init__(self):
        self._databases = []

    def init(self):
        def decorator(func: Callable):
            self._databases.append(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    async def start(self):
        try:
            for db in self._databases:
                await db()
            logger.success('初始化数据库成功')
        except Exception as e:
            logger.error('初始化数据库失败: ' + str(e))
            exit()
