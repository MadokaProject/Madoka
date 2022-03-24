from arclet.alconna import Alconna, Option, Arpamar
from graia.ariadne.model import MemberPerm

from app.console.base import ConsoleController
from app.core.command_manager import CommandManager


class InfoList(ConsoleController):
    entry = 'list'
    brief_help = '查看好友/群组信息'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(
        command=entry,
        options=[
            Option('--friend', alias='-f', help_text='查看好友信息'),
            Option('--group', alias='-g', help_text='查看群组信息')
        ],
        help_text=brief_help
    ))
    async def process(self, command: Arpamar):
        if command.has('friend'):
            return '\n'.join(
                f'{friend.remark}({friend.id})' + (f' - {friend.nickname}' if friend.nickname != friend.remark else '')
                for friend in await self.app.getFriendList())
        elif command.has('group'):
            return '\n'.join(f'{group.name}({group.id}) - {self.get_perm_name(group.accountPerm)}' for group in
                             await self.app.getGroupList())
        return self.args_error()

    @classmethod
    def get_perm_name(cls, perm: MemberPerm):
        if perm == MemberPerm.Member:
            return '群成员'
        elif perm == MemberPerm.Administrator:
            return '管理员'
        elif perm == MemberPerm.Owner:
            return '群主'
