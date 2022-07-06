import functools
from types import ModuleType
from typing import Dict, Union, Optional, List

from arclet.alconna import Alconna, command_manager as _cmd_mgr

from app.core.config import Config
from app.util.decorator import ArgsAssigner, Singleton


class PluginInfo:
    def __init__(self, entry, brief_help, enable: bool, hidden: bool, alc: Alconna, func):
        self.entry: str = entry
        self.brief_help: str = brief_help
        self.enable: bool = enable
        self.hidden: bool = hidden
        self.alc: Alconna = alc
        self.func = func


class CommandDelegateManager(metaclass=Singleton):
    """
    Alconna 命令委托管理器
    """
    __delegates: Dict[str, Dict[str, PluginInfo]]
    headers: List[str] = Config().COMMAND_HEADERS

    def __init__(self):
        self.__delegates = {}

    @staticmethod
    def get_commands(namespace: Optional[str] = None):
        try:
            return _cmd_mgr.get_commands(namespace)
        except KeyError:
            return []

    def from_path(self, path: str, cmd_type: str = 'plugin') -> Optional[Alconna]:
        if self.__delegates.get(cmd_type) and self.__delegates[cmd_type].get(path):
            return self.get_delegate(path, cmd_type).alc

    def add_delegate(self, path: str, func: PluginInfo, cmd_type: str = 'plugin'):
        self.__delegates[cmd_type] = {path: func}

    def get_delegate(self, path: str, cmd_type: str = 'plugin') -> Optional[PluginInfo]:
        return self.__delegates[cmd_type].get(path)

    def get_delegates(self, cmd_type: str = 'plugin') -> Dict[str, PluginInfo]:
        return self.__delegates.get(cmd_type)

    def get_all_delegates(self) -> Dict[str, PluginInfo]:
        return {k: v for i in self.__delegates.values() for k, v in i.items()}

    def register(
            self,
            entry: str,
            brief_help: str,
            alc: Alconna,
            enable: bool = True,
            hidden: bool = False,
            many: int = 0
    ):
        """注册命令

        :param entry: 命令入口
        :param brief_help: 插件简介
        :param alc: Alconna 实例
        :param enable: 是否启用
        :param hidden: 是否隐藏
        :param many: 插件序号: 仅单文件多插件时使用（不推荐单文件多插件，暂时无法管理）
        """

        def decorator(func):
            @ArgsAssigner
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            module = func.__module__
            path_parts = module.split('.')
            alc.reset_namespace(f'{path_parts[-3]}_{path_parts[-2]}')
            if not self.__delegates.get(path_parts[-4]):
                self.__delegates[path_parts[-4]] = {}
            if many:
                module += str(many)

            _plg_info = PluginInfo(entry, brief_help, enable, hidden, alc, wrapper)
            self.__delegates[path_parts[-4]].update({module: _plg_info})
            return wrapper

        return decorator

    def delete(self, target: Union[PluginInfo, ModuleType], cmd_type: str = 'plugin') -> None:
        """删除命令"""
        if isinstance(target, PluginInfo):
            _cmd_mgr.delete(target.alc)
            target = target.func.__module__
        elif isinstance(target, ModuleType):
            target = target.__name__
            if target in self.__delegates[cmd_type]:
                _cmd_mgr.delete(self.__delegates[cmd_type][target].alc)
        try:
            del self.__delegates[cmd_type][target]
        except KeyError:
            pass
