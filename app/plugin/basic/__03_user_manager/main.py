from typing import Union

from app.util.alconna import Args, Arpamar, Commander, Option
from app.util.control import Permission
from app.util.graia import Ariadne, Friend, Group, message

command = Commander(
    "am",
    "账号管理",
    Option("list", Args["type", ["friend", "group", "f", "g"]], help_text="列出好友、群列表"),
    Option("delete", Args["type", ["friend", "group", "f", "g"]]["id", int], help_text="删除好友、群"),
    hidden=True,
)


@command.parse("list", permission=Permission.MASTER)
async def list(app: Ariadne, cmd: Arpamar, sender: Union[Friend, Group]):
    rs_type = cmd.get("type")
    if rs_type in ["friend", "f"]:
        friend_list = await app.get_friend_list()
        msg = message(
            "\n".join(f"好友ID：{str(friend.id).ljust(14)}好友昵称：{str(friend.nickname)}" for friend in friend_list)
        )
    else:
        group_list = await app.get_group_list()
        msg = message("\n".join(f"群ID：{str(group.id).ljust(14)}群名：{group.name}" for group in group_list))
    msg.target(sender).send()


@command.parse("delete", permission=Permission.MASTER)
async def delete(app: Ariadne, cmd: Arpamar, sender: Union[Friend, Group]):
    rs_type = cmd.get("type")
    target_id = cmd.get("id")
    if rs_type in ["friend", "f"]:
        if await app.get_friend(target_id):
            await app.delete_friend(target_id)
            msg = "成功删除该好友！"
        else:
            msg = "没有找到该好友！"
    else:
        if await app.get_group(target_id):
            await app.quit_group(target_id)
            msg = "成功退出该群组！"
        else:
            msg = "没有找到该群组！"
    return message(msg).target(sender).send()
