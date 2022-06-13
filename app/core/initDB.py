from functools import wraps
from typing import Callable, List

from loguru import logger


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
            raise Exception

    @classmethod
    def get_instance(cls):
        if cls.__instance:
            return cls.__instance
        else:
            raise Exception

    def __call__(self):
        def decorator(func: Callable):
            self.__databases.append(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def start(self):
        try:
            for db in self.__databases:
                db()
            logger.success('初始化数据库成功')
        except Exception as e:
            logger.error('初始化数据库失败: ' + str(e))
            exit()
