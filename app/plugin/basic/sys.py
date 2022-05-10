from arclet.alconna import Alconna, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config


class Module(Plugin):
    entry = 'sys'
    brief_help = '系统'
    hidden = True
    manager: CommandDelegateManager = CommandDelegateManager.get_instance()
    configs = {'禁言退群': 'bot_mute_event', '上线通知': 'online_notice'}

    @permission_required(level=Permission.MASTER)
    @manager.register(
        Alconna(
            headers=manager.headers,
            command=entry,
            options=[
                Option('禁言退群', help_text='设置机器人禁言是否退群', args=Args['bool': bool]),
                Option('上线通知', help_text='设置机器人上线是否通知该群', args=Args['bool': bool])
            ],
            help_text='系统设置: 仅主人可用!'
        )
    )
    async def process(self, command: Arpamar, alc: Alconna):
        options = command.options
        if not options:
            return await self.print_help(alc.get_help())
        try:
            if not hasattr(self, 'group'):
                return MessageChain.create([Plain('请在群聊内使用该命令!')])
            config_name = self.configs[list(options.keys())[0]]
            if await save_config(config_name, self.group.id, command.query('bool')):
                return MessageChain.create([Plain('开启成功！' if command.query('bool') else '关闭成功！')])
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()
