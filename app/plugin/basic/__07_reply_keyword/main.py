from typing import Union

from arclet.alconna import Alconna, Option, Args, Arpamar, AllParam
from graia.ariadne.model import Friend, Group, Member
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.util.control import Permission
from app.util.online_config import save_config, get_config
from app.util.phrases import *

manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry='reply',
    brief_help='群自定义回复',
    alc=Alconna(
        headers=manager.headers,
        command='reply',
        options=[
            Option('add', help_text='添加或修改自定义回复', args=Args['keyword', str]['text', AllParam]),
            Option('remove', help_text='删除自定义回复', args=Args['keyword', str]),
            Option('list', help_text='列出本群自定义回复')
        ],
        help_text='群自定义回复: 仅管理可用!'
    )
)
@Permission.require(level=Permission.GROUP_ADMIN)
async def process(sender: Union[Friend, Group], command: Arpamar, alc: Alconna, _: Union[Friend, Member]):
    options = command.options
    if not options:
        return await print_help(alc.get_help())
    try:
        if not isinstance(sender, Group):
            return MessageChain([Plain('请在群聊内使用该命令!')])
        if add := options.get('add'):
            await save_config('group_reply', sender, {
                add['keyword']: '\n'.join(v for v in add['text'])
            }, model='add')
            return MessageChain([Plain('添加/修改成功！')])
        elif remove := options.get('remove'):
            await save_config('group_reply', sender, remove['keyword'], model='remove')
            return MessageChain('删除成功!')
        elif options.get('list'):
            res = await get_config('group_reply', sender)
            return MessageChain(
                [Plain('\n'.join(f'{key}' for key in res.keys()) if res else '该群组暂未配置！')]
            )
        return args_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()
