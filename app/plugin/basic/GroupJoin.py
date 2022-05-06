from arclet.alconna import Alconna, Option, Args, Arpamar, AllParam
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config, get_config


class Module(Plugin):
    entry = 'join'
    brief_help = '入群欢迎'
    manager: CommandDelegateManager = CommandDelegateManager.get_instance()

    @permission_required(level=Permission.GROUP_ADMIN)
    @manager.register(
        Alconna(
            headers=manager.headers,
            command=entry,
            options=[
                Option('set', help_text='设置入群欢迎消息', args=Args['msg': AllParam]),
                Option('view', help_text='查看入群欢迎消息'),
                Option('status', help_text='开关入群欢迎', args=Args['bool': bool])
            ],
            help_text='入群欢迎(仅管理可用)'
        )
    )
    async def process(self, command: Arpamar, alc: Alconna):
        options = command.options
        if not options:
            return await self.print_help(alc.get_help())
        try:
            if not hasattr(self, 'group'):
                return MessageChain.create([Plain('请在群组使用该命令!')])
            if set_ := options.get('set'):
                await save_config('member_join', self.group.id, {
                    'active': 1,
                    'text': '\n'.join([f'{value}' for value in set_['msg']])
                })
                return MessageChain.create([Plain('设置成功！')])
            elif 'view' in options:
                res = await get_config('member_join', self.group.id)
                if not res:
                    return MessageChain.create([Plain("该群组未配置欢迎消息！")])
                return MessageChain.create([
                    Plain(f"欢迎消息：{res['text'] if res.__contains__('text') else '默认欢迎消息'}"),
                    Plain(f"\n开启状态：{res['active']}")
                ])
            elif status := options.get('status'):
                await save_config('member_join', self.group.id, {'active': status['bool']}, model='add')
                return MessageChain.create([Plain("开启成功!" if status['bool'] else '关闭成功!')])
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
