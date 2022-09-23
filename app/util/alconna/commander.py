import traceback
from functools import wraps
from typing import Callable, Union

from arclet.alconna import Alconna, Args, Arpamar, CommandMeta, Option, Subcommand

from ..decorator import ArgsAssigner
from ..graia import (
    Ariadne,
    Friend,
    Group,
    InterruptControl,
    Member,
    MessageChain,
    Source,
)


class Commander:
    """对 Alconna 进行部分封装，简化命令的注册过程。

    Typical usage example:
    >>> from app.util.alconna import Commander, Subcommand, Arpamar
    >>> command = Commander(
            "test",
            "测试",
            Subcommand("test1", help_text="test1"),
            Subcommand("test2", help_text="test2")
        )
    >>>
    >>> @command.parse("test1")
    >>> async def test1(result: Arpamar, *args, **kwargs):
    >>>    pass
    >>>
    >>> @command.parse("test2")
    >>> async def test2(result: Arpamar, *args, **kwargs):
    >>>    pass
    """

    options: dict[str, Callable] = {}

    def __init__(
        self,
        entry,
        brief_help: str,
        *args: Union[Args, Option, Subcommand],
        help_text: str = None,
        enable: bool = True,
        hidden: bool = False,
        **kwargs,
    ):
        self.entry = entry
        self.brief_help = brief_help
        self.help_text = help_text or brief_help
        self.enable = enable
        self.hidden = hidden
        self.alconna = Alconna(entry, *args, meta=CommandMeta(self.help_text), **kwargs)
        self.module_name = ".".join(traceback.extract_stack()[-2][0].strip(".py").split("/")[-5:])
        from app.core.commander import CommandDelegateManager

        manager: CommandDelegateManager = CommandDelegateManager()

        @manager.register(self.entry, self.brief_help, self.alconna, self.enable, self.hidden, self.module_name)
        async def process(
            app: Ariadne,
            message: MessageChain,
            target: Union[Friend, Member],
            sender: Union[Friend, Group],
            source: Source,
            inc: InterruptControl,
            result: Arpamar,
        ):
            for name, func in self.options.items():
                if result.find(name):
                    await func(app, message, target, sender, source, inc, result)

    def parse(self, name: str):
        def wrapper(func):
            @ArgsAssigner
            @wraps(func)
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            self.options[name] = inner
            return inner

        return wrapper
