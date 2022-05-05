import functools
import inspect
from typing import Dict, Union, Callable, Optional
from types import ModuleType

from arclet.alconna import Alconna, command_manager as _cmd_mgr
from arclet.alconna.util import Singleton

from .Exceptions import CommandManagerInitialized, CommandManagerAlreadyInitialized, NonStandardPlugin


class CommandDelegateManager(metaclass=Singleton):
    """
    Alconna 命令委托管理器
    """
    __first_init: bool = False
    __delegates: Dict[str, Callable]
    headers = ['.', ',', ';', '!', '?', '。', '，', '；', '！', '？', '/', '\\']

    def __init__(self):
        if not self.__first_init:
            self.__delegates = {}
            self.__first_init = True
        else:
            raise CommandManagerAlreadyInitialized("命令管理器重复初始化")

    @classmethod
    def get_instance(cls):
        if cls.__first_init:
            return cls()
        else:
            raise CommandManagerInitialized("命令管理器未初始化")

    @staticmethod
    def get_commands(namespace: Optional[str] = None):
        try:
            return _cmd_mgr.get_commands(namespace)
        except KeyError:
            return []

    def from_path(self, path: str) -> Optional[Alconna]:
        if self.__delegates.get(path):
            return _cmd_mgr.get_command(path)

    def add_delegate(self, alc: Alconna, func: Callable):
        self.__delegates[alc.path] = func

    def get_delegate(self, path: str) -> Optional[Callable]:
        return self.__delegates.get(path)

    def register(self, alc: Alconna):
        """注册命令"""

        def decorator(func: Callable):
            path_parts = inspect.getfile(func).replace('\\', '/').split('/')
            alc.reset_namespace(f'{path_parts[-3]}.{path_parts[-2]}')
            self.__delegates[alc.path] = func

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def delete(self, target: Union[Alconna, ModuleType]) -> None:
        """删除命令"""
        if isinstance(target, Alconna):
            _cmd_mgr.delete(target)
        else:
            module_path = target.__name__.split('.')
            namespace = f'{module_path[-3]}.{module_path[-2]}'
            try:
                name = target.Module.entry
            except AttributeError:
                raise NonStandardPlugin("Madoka 插件必须以 'Module' 为名称作为入口")
            if alc := self.__delegates.get(f"{namespace}.{name}"):
                _cmd_mgr.delete(alc)
                target = alc
        try:
            del self.__delegates[target.path]
        except KeyError:
            pass


command_manager = CommandDelegateManager()
