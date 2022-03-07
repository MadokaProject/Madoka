import functools
import inspect
from typing import Dict, Union, Any

from arclet.alconna import Alconna, command_manager as CM

from .Exceptions import CommandManagerInitialized, CommandManagerAlreadyInitialized


class CommandManager:
    """命令管理器"""
    __instance = None
    __first_init: bool = False
    __commands: Dict[str, Dict[Alconna, str]]
    headers = ['.', ',', ';', '!', '?', '。', '，', '；', '！', '？', '/', '\\']

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__first_init:
            self.__commands = {}
        else:
            raise CommandManagerAlreadyInitialized("命令管理器重复初始化")

    @classmethod
    def get_command_instance(cls):
        if cls.__instance:
            return cls.__instance
        else:
            raise CommandManagerInitialized("命令管理器未初始化")

    def get_commands(self):
        return self.__commands

    def register(self, command: Alconna, func) -> None:
        if command.namespace not in self.__commands:
            self.__commands[command.namespace] = {}
        self.__commands[command.namespace].update({command: func})

    def delete(self, command: Union[Alconna, Any]) -> None:
        """删除命令"""
        if isinstance(command, Alconna):
            namespace = command.namespace
            CM.delete(command)
        else:
            command_name = command.__name__.split('.')
            namespace = f'{command_name[-3]}.{command_name[-2]}'
            for alc in self.__commands[namespace]:
                if alc.command == command.Module.entry:
                    CM.delete(alc)
                    command = alc
                    break
        try:
            del self.__commands[namespace][command]
        finally:
            if self.__commands[namespace] == {}:
                del self.__commands[namespace]
            return None

    def __call__(self, alc: Alconna):
        def decorator(func):
            namespace = inspect.getfile(func).split('\\')[-3:-1]
            alc.reset_namespace(f'{namespace[0]}.{namespace[1]}')
            self.register(alc, func.__name__)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator


command_manager = CommandManager()
