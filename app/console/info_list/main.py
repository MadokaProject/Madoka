from arclet.alconna import Alconna, Arpamar, Option
from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.model import MemberPerm

from app.console.util import args_error, send
from app.core.app import AppCore

con: Console = AppCore().get_console()
alc = Alconna(
    command="list",
    options=[
        Option("--friend|-f", help_text="查看好友信息"),
        Option("--group|-g", help_text="查看群组信息"),
    ],
    help_text="查看好友/群组信息",
)


@con.register([AlconnaDispatcher(alc)])
async def process(app: Ariadne, cmd: Arpamar):
    if not cmd.matched:
        return send(alc.help_text)
    if cmd.find("friend"):
        return send(
            "\n".join(
                f"{friend.remark}({friend.id})" + (f" - {friend.nickname}" if friend.nickname != friend.remark else "")
                for friend in (await app.get_friend_list())
            )
        )
    elif cmd.find("group"):
        return send(
            "\n".join(
                f"{group.name}({group.id}) - {get_perm_name(group.account_perm)}"
                for group in (await app.get_group_list())
            )
        )
    return args_error()


def get_perm_name(perm: MemberPerm):
    if perm == MemberPerm.Member:
        return "群成员"
    elif perm == MemberPerm.Administrator:
        return "管理员"
    elif perm == MemberPerm.Owner:
        return "群主"
