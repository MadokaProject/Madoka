from graia.ariadne.model import MemberPerm

from app.console.base import ConsoleController
from app.util.tools import isstartswith


class InfoList(ConsoleController):
    entry = 'list'
    brief_help = '查看好友/群组信息'
    full_help = {
        '-g, --group': '查看群组信息',
        '-f, --friend': '查看好友信息'
    }

    @classmethod
    def get_perm_name(cls, perm: MemberPerm):
        if perm == MemberPerm.Member:
            return '群成员'
        elif perm == MemberPerm.Administrator:
            return '管理员'
        elif perm == MemberPerm.Owner:
            return '群主'

    async def process(self):
        if not self.param:
            self.print_help()
            return
        if isstartswith(self.param[0], ['-g', '--group']):
            self.resp = '\n'.join(f'{group.name}({group.id}) - {self.get_perm_name(group.accountPerm)}' for group in
                                  await self.app.getGroupList())
        elif isstartswith(self.param[0], ['-f', '--friend']):
            self.resp = '\n'.join(
                f'{friend.remark}({friend.id})' + (f' - {friend.nickname}' if friend.nickname != friend.remark else '')
                for friend in await self.app.getFriendList())
        else:
            self.args_error()
