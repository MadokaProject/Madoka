from arclet.alconna import AllParam

from app.util.alconna import Args, Arpamar, Commander, Option
from app.util.control import Permission
from app.util.graia import Group, GroupMessage, message
from app.util.online_config import get_config, save_config

command = Commander(
    "reply",
    "群自定义回复",
    Option("add", help_text="添加或修改自定义回复", args=Args["keyword", str]["text", AllParam]),
    Option("remove", help_text="删除自定义回复", args=Args["keyword", str]),
    Option("list", help_text="列出本群自定义回复"),
    help_text="群自定义回复: 仅管理可用!",
)


@command.parse("add", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def add_reply(sender: Group, cmd: Arpamar):
    await save_config("group_reply", sender, {cmd.query("keyword"): "\n".join(cmd.query("text"))}, model="add")
    return message("添加/修改成功！").target(sender).send()


@command.parse("remove", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def remove_reply(sender: Group, cmd: Arpamar):
    await save_config("group_reply", sender, cmd.query("keyword"), model="remove")
    return message("删除成功！").target(sender).send()


@command.parse("list", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def list_reply(sender: Group):
    res = await get_config("group_reply", sender)
    return message("\n".join(f"{key}" for key in res.keys()) if res else "该群组暂未配置！").target(sender).send()
