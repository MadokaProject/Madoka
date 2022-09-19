from typing import Union

from arclet.alconna import Alconna, Args, Arpamar, CommandMeta, Option
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group, Member
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.util.control import Permission
from app.util.online_config import save_config
from app.util.phrases import print_help, unknown_error

manager: CommandDelegateManager = CommandDelegateManager()
configs = {"禁言退群": "bot_mute_event", "上线通知": "online_notice"}


@manager.register(
    entry="sys",
    brief_help="系统",
    hidden=True,
    alc=Alconna(
        "sys",
        Option("禁言退群", help_text="设置机器人禁言是否退群", args=Args["bool", bool]),
        Option("上线通知", help_text="设置机器人上线是否通知该群", args=Args["bool", bool]),
        meta=CommandMeta("系统设置: 仅主人可用!"),
    ),
)
@Permission.require(level=Permission.MASTER)
async def process(sender: Union[Friend, Group], cmd: Arpamar, alc: Alconna, _: Union[Friend, Member]):
    options = cmd.options
    if not options:
        return await print_help(alc.get_help())
    try:
        if not isinstance(sender, Group):
            return MessageChain([Plain("请在群聊内使用该命令!")])
        await save_config(configs[list(options.keys())[0]], sender.id, cmd.query("bool"))
        return MessageChain([Plain("开启成功！" if cmd.query("bool") else "关闭成功！")])
    except Exception as e:
        logger.exception(e)
        return unknown_error()
