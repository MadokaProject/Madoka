from arclet.alconna import Alconna, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.console.base import ConsoleController
from app.core.commander import CommandDelegateManager

entry = 'send'
brief_help = '发送消息'
manager: CommandDelegateManager = CommandDelegateManager.get_instance()


@manager.register(
    entry=entry,
    brief_help=brief_help,
    alc=Alconna(
        command=entry,
        options=[
            Option('--friend|-f', help_text='向指定好友发送消息', args=Args['num': int]),
            Option('--group|-g', help_text='向指定群组发送消息', args=Args['num': int])
        ],
        help_text='发送消息',
        main_args=Args['msg': str]
    )
)
async def process(self: ConsoleController, command: Arpamar):
    if frd := command.options.get('friend'):
        if await self.app.getFriend(frd['num']):
            await self.app.sendFriendMessage(
                frd['num'], MessageChain.create(Plain(command.query('msg')))
            )
            return '发送成功!'
        return '未找到该好友'
    elif gp := command.options.get('group'):
        if await self.app.getGroup(gp['num']):
            await self.app.sendGroupMessage(
                gp['num'], MessageChain.create(Plain(command.query('msg')))
            )
            return '发送成功!'
        return '未找到该群组'
    return self.args_error()
