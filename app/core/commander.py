import contextlib
import functools
from types import ModuleType
from typing import Callable, Optional, Union

from arclet.alconna import Alconna
from arclet.alconna import command_manager as _cmd_mgr
from arclet.alconna.graia.analyser import GraiaCommandAnalyser

from app.util.alconna import set_default_namespace
from app.util.decorator import ArgsAssigner, Singleton

set_default_namespace(name="plugin")
Alconna.config(analyser_type=GraiaCommandAnalyser)


class PluginInfo:
    def __init__(self, entry, brief_help, enable: bool, hidden: bool, alc: Alconna, func):
        self.entry: str = entry
        self.brief_help: str = brief_help
        self.enable: bool = enable
        self.hidden: bool = hidden
        self.alc: Alconna = alc
        self.func = func


class CommandDelegateManager(metaclass=Singleton):
    """Alconna 命令委托管理器"""

    __delegates: dict[str, dict[str, PluginInfo]]

    def __init__(self):
        self.__delegates = {}

    @staticmethod
    def get_commands(namespace: Optional[str] = None):
        try:
            return _cmd_mgr.get_commands(namespace)
        except KeyError:
            return []

    def from_path(self, path: str, cmd_type: str = "plugin") -> Optional[Alconna]:
        if self.__delegates.get(cmd_type) and self.__delegates[cmd_type].get(path):
            return self.get_delegate(path, cmd_type).alc

    def add_delegate(self, path: str, func: PluginInfo, cmd_type: str = "plugin"):
        self.__delegates[cmd_type] = {path: func}

    def get_delegate(self, path: str, cmd_type: str = "plugin") -> Optional[PluginInfo]:
        return self.__delegates[cmd_type].get(path)

    def get_delegates(self, cmd_type: str = "plugin") -> dict[str, PluginInfo]:
        return self.__delegates.get(cmd_type)

    def get_all_delegates(self) -> dict[str, PluginInfo]:
        return {k: v for i in self.__delegates.values() for k, v in i.items()}

    def register(
        self,
        entry: str,
        brief_help: str,
        alc: Alconna,
        enable: bool = True,
        hidden: bool = False,
        module_name: str = None,
    ):
        """注册命令

        :param entry: 命令入口
        :param brief_help: 插件简介
        :param alc: Alconna 实例
        :param enable: 是否启用
        :param hidden: 是否隐藏
        :param module_name: 使用Commander装饰的模块
        """

        def decorator(func: Callable):
            @ArgsAssigner
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            module = module_name or func.__module__
            path_parts = module.split(".")

            if not self.__delegates.get(path_parts[1]):
                self.__delegates[path_parts[1]] = {}
            elif self.__delegates[path_parts[1]].get(module):
                raise RuntimeError("禁止单文件注册多个命令")

            plg_info = PluginInfo(entry, brief_help, enable, hidden, alc, wrapper)
            self.__delegates[path_parts[1]][module] = plg_info
            return wrapper

        return decorator

    def delete(self, target: Union[PluginInfo, ModuleType], cmd_type: str = "plugin") -> None:
        """删除命令"""
        if isinstance(target, PluginInfo):
            _cmd_mgr.delete(target.alc)
            target = target.func.__module__
        elif isinstance(target, ModuleType):
            target = target.__name__
            if target in self.__delegates[cmd_type]:
                _cmd_mgr.delete(self.__delegates[cmd_type][target].alc)
        with contextlib.suppress(KeyError):
            del self.__delegates[cmd_type][target]
