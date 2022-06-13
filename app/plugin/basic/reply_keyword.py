from arclet.alconna import Alconna, Option, Args, Arpamar, AllParam
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.online_config import save_config, get_config

manager: CommandDelegateManager = CommandDelegateManager.get_instance()


@permission_required(level=Permission.GROUP_ADMIN)
@manager.register(
    entry='reply',
    brief_help='群自定义回复',
    alc=Alconna(
        headers=manager.headers,
        command='reply',
        options=[
            Option('add', help_text='添加或修改自定义回复', args=Args['keyword': str, 'text': AllParam]),
            Option('remove', help_text='删除自定义回复', args=Args['keyword': str]),
            Option('list', help_text='列出本群自定义回复')
        ],
        help_text='群自定义回复: 仅管理可用!'
    )
)
async def process(self: Plugin, command: Arpamar, alc: Alconna):
    options = command.options
    if not options:
        return await self.print_help(alc.get_help())
    try:
        if not hasattr(self, 'group'):
            return MessageChain.create([Plain('请在群聊内使用该命令!')])
        if add := options.get('add'):
            await save_config('group_reply', self.group.id, {
                add['keyword']: add['text'][0].replace('<br>', '\n')
            }, model='add')
            return MessageChain.create([Plain('添加/修改成功！')])
        elif remove := options.get('remove'):
            msg = '删除成功!' if (await save_config(
                'group_reply', self.group.id, remove['keyword'], model='remove'
            )) else '删除失败!该关键词不存在'
            return MessageChain.create([Plain(msg)])
        elif options.get('list'):
            res = await get_config('group_reply', self.group.id)
            return MessageChain.create(
                [Plain('\n'.join(f'{key}' for key in res.keys()) if res else '该群组暂未配置！')]
            )
        return self.args_error()
    except Exception as e:
        logger.exception(e)
        return self.unkown_error()
