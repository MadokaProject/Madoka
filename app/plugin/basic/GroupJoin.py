from arclet.alconna import Alconna, Subcommand, Args, Arpamar, AllParam
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.command_manager import CommandManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config, get_config


class Module(Plugin):
    entry = 'join'
    brief_help = '入群欢迎'
    manager: CommandManager = CommandManager.get_command_instance()

    @permission_required(level=Permission.GROUP_ADMIN)
    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('set', help_text='设置入群欢迎消息', args=Args['msg': AllParam]),
            Subcommand('view', help_text='查看入群欢迎消息'),
            Subcommand('status', help_text='开关入群欢迎', args=Args['bool': bool])
        ],
        help_text='入群欢迎(仅管理可用)'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        other_args = command.other_args
        if not subcommand:
            return await self.print_help(alc.get_help())
        try:
            if not hasattr(self, 'group'):
                return MessageChain.create([Plain('请在群组使用该命令!')])
            if subcommand.__contains__('set'):
                await save_config('member_join', self.group.id, {
                    'active': 1,
                    'text': '\n'.join([f'{value}' for value in other_args['msg']])
                })
                return MessageChain.create([Plain('设置成功！')])
            elif subcommand.__contains__('view'):
                res = await get_config('member_join', self.group.id)
                if not res:
                    return MessageChain.create([Plain("该群组未配置欢迎消息！")])
                return MessageChain.create([
                    Plain(f"欢迎消息：{res['text'] if res.__contains__('text') else '默认欢迎消息'}"),
                    Plain(f"\n开启状态：{res['active']}")
                ])
            elif subcommand.__contains__('status'):
                await save_config('member_join', self.group.id, {'active': other_args['bool']}, model='add')
                return MessageChain.create([Plain("开启成功!" if other_args['bool'] else '关闭成功!')])
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
