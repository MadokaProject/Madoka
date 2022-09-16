from typing import Union

from arclet.alconna import Alconna, AllParam, Args, Arpamar, Option
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group, Member
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.util.control import Permission
from app.util.online_config import get_config, save_config
from app.util.phrases import args_error, print_help, unknown_error

manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry="join",
    brief_help="入群欢迎",
    alc=Alconna(
        headers=manager.headers,
        command="join",
        options=[
            Option("set", help_text="设置入群欢迎消息", args=Args["msg", AllParam]),
            Option("view", help_text="查看入群欢迎消息"),
            Option("status", help_text="开关入群欢迎", args=Args["bool", bool]),
        ],
        help_text="入群欢迎(仅管理可用)",
    ),
)
@Permission.require(level=Permission.GROUP_ADMIN)
async def process(
    sender: Union[Friend, Group],
    command: Arpamar,
    alc: Alconna,
    _: Union[Friend, Member],
):
    options = command.options
    if not options:
        return await print_help(alc.get_help())
    try:
        if not isinstance(sender, Group):
            return MessageChain([Plain("请在群组使用该命令!")])
        if set_ := options.get("set"):
            await save_config(
                "member_join",
                sender,
                {"active": 1, "text": "\n".join(v for v in set_["msg"])},
            )
            return MessageChain([Plain("设置成功！")])
        elif "view" in options:
            res = await get_config("member_join", sender)
            if not res:
                return MessageChain([Plain("该群组未配置欢迎消息！")])
            return MessageChain(
                [
                    Plain(f"欢迎消息：{res['text'] if res.__contains__('text') else '默认欢迎消息'}"),
                    Plain(f"\n开启状态：{res['active']}"),
                ]
            )
        elif status := options.get("status"):
            await save_config("member_join", sender, {"active": status["bool"]}, model="add")
            return MessageChain([Plain("开启成功!" if status["bool"] else "关闭成功!")])
        return args_error()
    except Exception as e:
        logger.exception(e)
        unknown_error()
