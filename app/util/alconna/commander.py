import time
import traceback
from functools import wraps
from typing import Callable, Optional, Type, Union

from arclet.alconna import Alconna, Args, Arpamar, CommandMeta, Option, Subcommand
from loguru import logger

from app.core.config import Config
from app.util.control import Permission
from app.util.decorator import ArgsAssigner
from app.util.exceptions.command import (
    AbortProcessError,
    FrequencyLimitError,
    FrequencyLimitExceededDoNothingError,
    FrequencyLimitExceededError,
)
from app.util.graia import (
    Ariadne,
    Friend,
    FriendMessage,
    Group,
    GroupMessage,
    InterruptControl,
    Member,
    MessageChain,
    Source,
    Stranger,
    StrangerMessage,
    TempMessage,
)
from app.util.phrases import print_help, unknown_error

_K_T = Type[Union[FriendMessage, GroupMessage, TempMessage, StrangerMessage]]


class Commander:
    """对 Alconna 进行部分封装，简化命令的注册过程。

    Examples:

    >>> from app.util.alconna import Commander, Subcommand, Arpamar
    >>> from app.util.graia import GroupMessage
    >>> command = Commander(
    ...     "test",
    ...     "测试",
    ...     Subcommand("test1", help_text="test1"),
    ...     Subcommand("test2", help_text="test2")
    ... )
    >>> @command.parse("test1")
    >>> async def test1(result: Arpamar, *args, **kwargs):
    ...    pass
    >>> @command.parse("test2", events=[GroupMessage])
    >>> async def test2(result: Arpamar, *args, **kwargs):
    ...    pass
    """

    __TypeMessage = {
        FriendMessage: Friend,
        GroupMessage: Group,
        TempMessage: Member,
        StrangerMessage: Stranger,
    }

    def __init__(
        self,
        entry,
        brief_help: str,
        *args: Union[Args, Option, Subcommand],
        command=None,
        help_text: str = None,
        enable: bool = True,
        hidden: bool = False,
        friend_limit: float = 0,
        group_limit: float = 0,
        **kwargs,
    ):
        """创建一个命令

        :param entry: 主命令
        :param brief_help: 简短帮助信息
        :param args: 命令选项
        :param command: 真·主命令，默认为 entry
        :param help_text: 帮助信息，默认为 brief_help
        :param enable: 插件开关，默认开启
        :param hidden: 隐藏插件，默认不隐藏
        :param friend_limit: 用户频率限制, 0不限制(该配置在群组也生效)
        :param group_limit: 群组频率限制, 0不限制
        """
        self.__entry = entry
        self.__brief_help = brief_help
        self.__command = command or entry
        self.__help_text = help_text or brief_help
        self.__enable = enable
        self.__hidden = hidden
        self.__friend_limit = friend_limit or Config.command.friend_limit
        self.__group_limit = group_limit or Config.command.group_limit
        self.alconna = Alconna(self.__command, *args, meta=CommandMeta(self.__help_text), **kwargs)
        self.__module_name = ".".join(traceback.extract_stack()[-2][0].strip(".py").replace("\\", "/").split("/")[-5:])
        self.__options: dict[str, Callable] = {}
        self.__no_match_action: Optional[Callable] = None
        self.__frequency_limit: dict[str, dict[int, float]] = {"friend": {}, "group": {}}
        assert all([self.__friend_limit >= 0, self.__group_limit >= 0]), "limit must be greater than or equal to 0"
        from app.core.commander import CommandDelegateManager

        manager: CommandDelegateManager = CommandDelegateManager()

        @manager.register(
            self.__entry, self.__brief_help, self.alconna, self.__enable, self.__hidden, self.__module_name
        )
        async def process(
            app: Ariadne,
            message: MessageChain,
            target: Union[Friend, Member],
            sender: Union[Friend, Group],
            source: Source,
            inc: InterruptControl,
            result: Arpamar,
        ):
            try:
                self.__is_frequency_limit__("__main__", self.__friend_limit, self.__group_limit, sender, target)
                for name, func in self.__options.items():
                    if result.find(name):
                        return await func(sender, target, app, message, target, sender, source, inc, result)
                if self.__no_match_action:
                    return await self.__no_match_action(
                        sender, target, app, message, target, sender, source, inc, result
                    )
                await print_help(sender, self.alconna.get_help())
            except FrequencyLimitError as e:
                logger.warning(e)
                return
            except AbortProcessError as e:
                logger.info(e)
                return
            except Exception as e:
                logger.exception(e)
                return unknown_error(sender)

    @staticmethod
    def __filter__(events: tuple):
        """事件过滤器"""

        def wrapper(func: Callable):
            @wraps(func)
            def inner(sender, *args, **kwargs):
                if isinstance(sender, events):
                    return func(*args, **kwargs)
                raise AbortProcessError("事件不匹配")

            return inner

        return wrapper

    def __is_frequency_limit__(
        self,
        name: str,
        friend_limit: float,
        group_limit: float,
        sender: Union[Friend, Group],
        target: Union[Friend, Member],
    ):
        now_time = time.time()
        if isinstance(sender, Group) and group_limit != 0:
            if name not in self.__frequency_limit["group"]:
                self.__frequency_limit["group"][name] = {}
            left_time = group_limit - (now_time - self.__frequency_limit["group"][name].get(sender.id, 0))
            if left_time > 0:
                raise FrequencyLimitExceededError(group_limit, left_time)
            self.__frequency_limit["group"][name][sender.id] = now_time
        if friend_limit != 0:
            if name not in self.__frequency_limit["friend"]:
                self.__frequency_limit["friend"][name] = {}
            left_time = friend_limit - (now_time - self.__frequency_limit["friend"][name].get(target.id, 0))
            if left_time > 0:
                raise FrequencyLimitExceededDoNothingError(friend_limit, left_time)
            self.__frequency_limit["friend"][name][target.id] = now_time

    def __frequency_limit__(self, name: str, friend_limit: float = 0, group_limit: float = 0):
        """设置频率限制

        :param name: 指定子命令
        :param friend_limit: 用户频率限制, 0不限制(该配置在群组也生效)
        :param group_limit: 群组频率限制, 0不限制
        """

        def wrapper(func: Callable):
            assert all([friend_limit >= 0, group_limit >= 0]), "limit must be greater than or equal to 0"

            @wraps(func)
            def inner(sender: Union[Friend, Group], target: Union[Friend, Member], *args, **kwargs):
                self.__is_frequency_limit__(name, friend_limit, group_limit, sender, target)
                return func(sender, *args, **kwargs)

            return inner

        return wrapper

    def no_match(
        self,
        /,
        events: list[_K_T] = None,
        permission: int = Permission.DEFAULT,
        friend_limit: float = 0,
        group_limit: float = 0,
    ):
        """无匹配子命令时的回调函数

        :param events: 事件过滤器，默认不过滤
        :param permission: 鉴权，默认允许黑名单外所有用户
        :param friend_limit: 用户频率限制, 0不限制(该配置在群组也生效)
        :param group_limit: 群组频率限制, 0不限制
        """

        def wrapper(func):
            @self.__frequency_limit__("__no_match__", friend_limit, group_limit)
            @self.__filter__(
                tuple(
                    [self.__TypeMessage[event] for event in events if event in self.__TypeMessage]
                    if events
                    else self.__TypeMessage.values()
                )
            )
            @Permission.require(permission)
            @ArgsAssigner
            @wraps(func)
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            self.__no_match_action = inner
            return inner

        return wrapper

    def parse(
        self,
        name: Union[str, list[str]],
        /,
        events: list[_K_T] = None,
        permission: int = Permission.DEFAULT,
        friend_limit: float = 0,
        group_limit: float = 0,
    ):
        """子命令匹配器

        :param name: 需要匹配的子命令
        :param events: 事件过滤器，默认不过滤
        :param permission: 鉴权，默认允许黑名单外所有用户
        :param friend_limit: 用户频率限制, 0不限制(该配置在群组也生效)
        :param group_limit: 群组频率限制, 0不限制
        """
        names = name if isinstance(name, list) else [name]

        def wrapper(func):
            @self.__frequency_limit__(names[0], friend_limit, group_limit)
            @self.__filter__(
                tuple(
                    [self.__TypeMessage[event] for event in events if event in self.__TypeMessage]
                    if events
                    else self.__TypeMessage.values()
                )
            )
            @Permission.require(permission)
            @ArgsAssigner
            @wraps(func)
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            for name in names:
                self.__options[name] = inner
            return inner

        return wrapper
