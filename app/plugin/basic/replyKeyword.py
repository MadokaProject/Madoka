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
    entry = 'reply'
    brief_help = '群自定义回复'
    manager: CommandManager = CommandManager.get_command_instance()

    @permission_required(level=Permission.GROUP_ADMIN)
    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('add', help_text='添加或修改自定义回复', args=Args['keyword': str, 'text': AllParam]),
            Subcommand('remove', help_text='删除自定义回复', args=Args['keyword': str]),
            Subcommand('list', help_text='列出本群自定义回复')
        ],
        help_text='群自定义回复: 仅管理可用!'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        other_args = command.other_args
        if not subcommand:
            return await self.print_help(alc.get_help())
        try:
            if not hasattr(self, 'group'):
                return MessageChain.create([Plain('请在群聊内使用该命令!')])
            if subcommand.__contains__('add'):
                await save_config('group_reply', self.group.id, {
                    other_args['keyword']: other_args['text'][0].replace('<br>', '\n')
                }, model='add')
                return MessageChain.create([Plain('添加/修改成功！')])
            elif subcommand.__contains__('remove'):
                msg = '删除成功!' if await save_config('group_reply', self.group.id, other_args['keyword'],
                                                   model='remove') else '删除失败!该关键词不存在'
                return MessageChain.create([Plain(msg)])
            elif subcommand.__contains__('list'):
                res = await get_config('group_reply', self.group.id)
                return MessageChain.create([Plain('\n'.join(f'{key}' for key in res.keys()) if res else '该群组暂未配置！')])
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()
