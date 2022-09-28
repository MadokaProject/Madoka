from arclet.alconna import AllParam

from app.util.alconna import Args, Arpamar, Commander, Option
from app.util.control import Permission
from app.util.graia import Group, GroupMessage, Plain, message
from app.util.online_config import get_config, save_config

command = Commander(
    "join",
    "入群欢迎",
    Option("set", help_text="设置入群欢迎消息", args=Args["msg", AllParam]),
    Option("view", help_text="查看入群欢迎消息"),
    Option("status", help_text="开关入群欢迎", args=Args["bool", bool]),
    help_text="入群欢迎(仅管理可用)",
)


@command.parse("set", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def set(sender: Group, cmd: Arpamar):
    await save_config("member_join", sender, {"active": 1, "text": "\n".join(cmd.query("msg"))})
    return message("设置成功！").target(sender).send()


@command.parse("view", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def view(sender: Group):
    res = await get_config("member_join", sender)
    return (
        message(
            [
                Plain(f"欢迎消息：{res['text'] if 'text' in res else '默认欢迎消息'}"),
                Plain(f"\n开启状态: {res['active']}"),
            ]
        )
        .target(sender)
        .send()
        if res
        else message("该群组未配置欢迎消息！").target(sender).send()
    )


@command.parse("status", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def status(sender: Group, cmd: Arpamar):
    await save_config("member_join", sender, {"active": cmd.query("bool")}, model="add")
    return message("开启成功!" if status["bool"] else "关闭成功!").target(sender).send()
