from arclet.alconna import Alconna, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.console.base import ConsoleController
from app.core.command_manager import CommandManager


class SendMsg(ConsoleController):
    entry = 'send'
    brief_help = '发送消息'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(
        command=entry,
        options=[
            Option('--friend', alias='-f', help_text='向指定好友发送消息', args=Args['num': int]),
            Option('--group', alias='-g', help_text='向指定群组发送消息', args=Args['num': int])
        ],
        help_text='发送消息',
        main_args=Args['msg': str]
    ))
    async def process(self, command: Arpamar):
        if command.options.__contains__('friend'):
            if await self.app.getFriend(command.other_args['num']):
                await self.app.sendFriendMessage(command.other_args['num'],
                                                 MessageChain.create(Plain(command.main_args['msg'])))
                return '发送成功!'
            return '未找到该好友'
        elif command.options.__contains__('group'):
            if await self.app.getGroup(command.other_args['num']):
                await self.app.sendGroupMessage(command.other_args['num'],
                                                MessageChain.create(Plain(command.main_args['msg'])))
                return '发送成功!'
            return '未找到该群组'
        return self.args_error()
