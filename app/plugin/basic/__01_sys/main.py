from typing import Union

from arclet.alconna import Alconna, Option, Args, Arpamar
from graia.ariadne.model import Friend, Group, Member
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.util.control import Permission
from app.util.online_config import save_config
from app.util.phrases import *

manager: CommandDelegateManager = CommandDelegateManager()
configs = {'禁言退群': 'bot_mute_event', '上线通知': 'online_notice'}


@manager.register(
    entry='sys',
    brief_help='系统',
    hidden=True,
    alc=Alconna(
        headers=manager.headers,
        command='sys',
        options=[
            Option('禁言退群', help_text='设置机器人禁言是否退群', args=Args['bool', bool]),
            Option('上线通知', help_text='设置机器人上线是否通知该群', args=Args['bool', bool])
        ],
        help_text='系统设置: 仅主人可用!'
    )
)
@Permission.require(level=Permission.MASTER)
async def process(sender: Union[Friend, Group], cmd: Arpamar, alc: Alconna, _: Union[Friend, Member]):
    options = cmd.options
    if not options:
        return await print_help(alc.get_help())
    try:
        if not isinstance(sender, Group):
            return MessageChain([Plain('请在群聊内使用该命令!')])
        config_name = configs[list(options.keys())[0]]
        if await save_config(config_name, sender.id, cmd.query('bool')):
            return MessageChain([Plain('开启成功！' if cmd.query('bool') else '关闭成功！')])
    except Exception as e:
        logger.exception(e)
        return unknown_error()
