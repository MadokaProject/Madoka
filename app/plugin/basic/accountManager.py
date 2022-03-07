from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.command_manager import CommandManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required


class Module(Plugin):
    entry = 'am'
    brief_help = '账号管理'
    hidden = True
    manager: CommandManager = CommandManager.get_command_instance()

    @permission_required(level=Permission.MASTER)
    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('list', help_text='列出好友、群列表', options=[
                Option('--friend', alias='-f', help_text='列出机器人的好友列表'),
                Option('--group', alias='-g', help_text='列出机器人的群组列表')
            ]),
            Subcommand('delete', help_text='删除好友、群', options=[
                Option('--friend', args=Args['friend_id': int], alias='-f', help_text='删除指定好友'),
                Option('--group', args=Args['group_id': int], alias='-g', help_text='退出指定群组')
            ])
        ],
        help_text='账号管理'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        other_args = command.other_args
        if not subcommand:
            return await self.print_help(alc.get_help())
        try:
            if subcommand.__contains__('list'):
                if other_args.__contains__('friend'):
                    friend_list = await self.app.getFriendList()
                    return MessageChain.create([
                        Plain('\r\n'.join(
                            f'好友ID：{str(friend.id).ljust(14)}好友昵称：{str(friend.nickname)}' for friend in friend_list))
                    ])
                if other_args.__contains__('group'):
                    group_list = await self.app.getGroupList()
                    return MessageChain.create([
                        Plain('\r\n'.join(f'群ID：{str(group.id).ljust(14)}群名：{group.name}' for group in group_list))
                    ])
            elif subcommand.__contains__('delete'):
                if other_args.__contains__('friend_id'):
                    if await self.app.getFriend(other_args['friend_id']):
                        await self.app.deleteFriend(other_args['friend_id'])
                        msg = '成功删除该好友！'
                    else:
                        msg = '没有找到该好友！'
                    return MessageChain.create([Plain(msg)])
                if other_args.__contains__('group_id'):
                    if await self.app.getGroup(other_args['group_id']):
                        await self.app.quitGroup(other_args['group_id'])
                        msg = '成功退出该群组！'
                    else:
                        msg = '没有找到该群组！'
                    return MessageChain.create([Plain(msg)])
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()
