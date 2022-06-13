from functools import wraps
from typing import Callable, List

from loguru import logger

from .exceptions import DatabaseManagerInitialized, DatabaseManagerAlreadyInitialized


class InitDB:
    __instance = None
    __first_init: bool = False
    __databases: List[Callable]

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__first_init:
            self.__databases = []
            self.__first_init = True
        else:
            raise DatabaseManagerAlreadyInitialized("数据库管理器重复初始化")

    @classmethod
    def get_instance(cls):
        if cls.__instance:
            return cls.__instance
        else:
            raise DatabaseManagerInitialized("数据库管理器未初始化")

    def init(self):
        def decorator(func: Callable):
            self.__databases.append(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    async def start(self):
        try:
            for db in self.__databases:
                await db()
            logger.success('初始化数据库成功')
        except Exception as e:
            logger.error('初始化数据库失败: ' + str(e))
            exit()
