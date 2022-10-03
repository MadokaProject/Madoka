import traceback
from functools import wraps
from typing import Callable, Union

from arclet.alconna import Alconna, Args, Arpamar, CommandMeta, Option, Subcommand
from loguru import logger

from app.util.control import Permission
from app.util.decorator import ArgsAssigner
from app.util.graia import (
    Ariadne,
    Friend,
    FriendMessage,
    Group,
    GroupMessage,
    InterruptControl,
    Member,
    MessageChain,
    MessageEvent,
    Source,
    Stranger,
    StrangerMessage,
    TempMessage,
)
from app.util.phrases import print_help, unknown_error


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
        """
        self.__entry = entry
        self.__brief_help = brief_help
        self.__command = command or entry
        self.__help_text = help_text or brief_help
        self.__enable = enable
        self.__hidden = hidden
        self.alconna = Alconna(self.__command, *args, meta=CommandMeta(self.__help_text), **kwargs)
        self.__module_name = ".".join(traceback.extract_stack()[-2][0].strip(".py").split("/")[-5:])
        self.__options: dict[str, Callable] = {}
        self.__no_match_action: Callable = None
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
                for name, func in self.__options.items():
                    if result.find(name):
                        return await func(sender, app, message, target, sender, source, inc, result)
                if self.__no_match_action:
                    return await self.__no_match_action(sender, app, message, target, sender, source, inc, result)
                await print_help(sender, self.alconna.get_help())
            except Exception as e:
                logger.exception(e)
                return unknown_error(sender)

    def __filter(self, events: tuple):
        """事件过滤器"""

        def wrapper(func: Callable):
            @wraps(func)
            def inner(sender, *args, **kwargs):
                if isinstance(sender, events):
                    return func(*args, **kwargs)

            return inner

        return wrapper

    def no_match(self, /, events: list[MessageEvent] = [], permission: int = Permission.DEFAULT):
        """无匹配子命令时的回调函数

        :param events: 事件过滤器，默认不过滤
        :param permission: 鉴权，默认允许黑名单外所有用户
        """

        def wrapper(func):
            @self.__filter(
                tuple(
                    [self.__TypeMessage[event] for event in events if event in self.__TypeMessage]
                    or self.__TypeMessage.values()
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
        self, name: Union[str, list[str]], /, events: list[MessageEvent] = [], permission: int = Permission.DEFAULT
    ):
        """子命令匹配器

        :param name: 需要匹配的子命令
        :param events: 事件过滤器，默认不过滤
        :param permission: 鉴权，默认允许黑名单外所有用户
        """
        names = name if isinstance(name, list) else [name]

        def wrapper(func):
            @self.__filter(
                tuple(
                    [self.__TypeMessage[event] for event in events if event in self.__TypeMessage]
                    or self.__TypeMessage.values()
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
