from arclet.alconna import Alconna, Option
from arclet.alconna.graia import AlconnaDispatcher, AlconnaProperty
from graia.ariadne import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.model import MemberPerm

from app.console.util import *
from app.core.app import AppCore

con: Console = AppCore.get_core_instance().get_console()


@con.register([AlconnaDispatcher(
    Alconna(
        command='list',
        options=[
            Option('--friend|-f', help_text='查看好友信息'),
            Option('--group|-g', help_text='查看群组信息')
        ],
        help_text='查看好友/群组信息'
    )
)])
async def process(app: Ariadne, result: AlconnaProperty):
    arp = result.result
    if not arp.matched:
        return send(result.help_text)
    if arp.find('friend'):
        return send('\n'.join(
            f'{friend.remark}({friend.id})' + (f' - {friend.nickname}' if friend.nickname != friend.remark else '')
            for friend in (await app.get_friend_list())
        ))
    elif arp.find('group'):
        return send('\n'.join(
            f'{group.name}({group.id}) - {get_perm_name(group.account_perm)}'
            for group in (await app.get_group_list())
        ))
    return args_error()


def get_perm_name(perm: MemberPerm):
    if perm == MemberPerm.Member:
        return '群成员'
    elif perm == MemberPerm.Administrator:
        return '管理员'
    elif perm == MemberPerm.Owner:
        return '群主'
