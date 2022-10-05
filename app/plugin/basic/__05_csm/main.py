from app.util.alconna import Args, Arpamar, Commander, Option, Subcommand
from app.util.control import Permission
from app.util.graia import Ariadne, At, Group, GroupMessage, Source, message
from app.util.online_config import save_config
from app.util.phrases import exec_permission_error

command = Commander(
    "csm",
    "群管",
    Subcommand(
        "mute",
        args=Args["at;O", At],
        help_text="禁言指定群成员",
        options=[
            Option("--time|-t", args=Args["time", int, 10], help_text="禁言时间(分)"),
            Option("--all|-a", help_text="开启全员禁言"),
        ],
    ),
    Subcommand(
        "unmute", args=Args["at;O", At], help_text="取消禁言指定群成员", options=[Option("--all|-a", help_text="关闭全员禁言")]
    ),
    Subcommand(
        "func",
        args=Args["status", bool],
        help_text="功能开关",
        options=[
            Option("--card|-C", help_text="成员名片修改通知"),
            Option("--flash|-F", help_text="闪照识别"),
            Option("--recall|-R", help_text="撤回识别"),
            Option("--kick|-K", help_text="成员被踢通知"),
            Option("--quit|-Q", help_text="成员退群通知"),
        ],
    ),
    Option("status", args=Args["bool", bool], help_text="开关群管"),
    Option("kick", args=Args["at", At], help_text="踢出指定群成员"),
    Option("revoke", args=Args["id", int], help_text="撤回消息, id=消息ID, 自最后一条消息起算"),
    Option(
        "刷屏检测",
        args=Args["time", int]["mute_time", int]["reply", str],
        help_text="检测time内的3条消息是否刷屏; time: 秒, mute_time: 分钟, reply: 回复消息",
    ),
    Option(
        "重复消息",
        args=Args["time", int]["mute_time", int]["reply", str],
        help_text="检测time内的3条消息是否重复; time: 秒, mute_time: 分钟, reply: 回复消息",
    ),
    Option(
        "超长消息",
        args=Args["len", int]["mute_time", int]["reply", str],
        help_text="检测单消息是否超出设定的长度; len: 文本长度, mute_time: 分钟, reply: 回复消息",
    ),
    help_text="群管助手",
)


@command.parse("status", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def status(sender: Group, cmd: Arpamar):
    await save_config("status", sender, cmd.query("bool"))
    message(f"群管已{'开启' if cmd.query('bool') else '关闭'}").target(sender).send()


@command.parse("kick", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def kick(app: Ariadne, sender: Group, cmd: Arpamar):
    try:
        await app.kick_member(sender, cmd.query("at").target)
        message("飞机票快递成功!").target(sender).send()
    except PermissionError:
        return exec_permission_error(sender)


@command.parse("revoke", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def revoke(app: Ariadne, sender: Group, source: Source, cmd: Arpamar):
    try:
        await app.recall_message(source.id - cmd.query("id"), sender)
    except PermissionError:
        return exec_permission_error(sender)


@command.parse("mute", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def mute(app: Ariadne, sender: Group, cmd: Arpamar):
    try:
        if cmd.query("mute.all"):
            await app.mute_all(sender)
            message("已开启全员禁言").target(sender).send()
        elif cmd.find("at"):
            await app.mute_member(sender, cmd.query("at").target, (cmd.query("time") or 10) * 60)
            message("禁言成功").target(sender).send()
    except PermissionError:
        return exec_permission_error(sender)


@command.parse("unmute", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def unmute(app: Ariadne, sender: Group, cmd: Arpamar):
    try:
        if cmd.query("unmute.all"):
            await app.unmute_all(sender)
            message("已关闭全员禁言").target(sender).send()
        elif cmd.find("at"):
            await app.unmute_member(sender, cmd.query("at").target)
            message("取消禁言成功").target(sender).send()
    except PermissionError:
        return exec_permission_error(sender)


@command.parse("func", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def func(sender: Group, cmd: Arpamar):
    tag = None
    if cmd.query("func.card"):
        tag = "member_card_change"
    elif cmd.query("func.quit"):
        tag = "member_quit"
    elif cmd.query("func.kick"):
        tag = "member_kick"
    elif cmd.query("func.flash"):
        tag = "flash_png"
    elif cmd.query("func.recall"):
        tag = "member_recall"
    if tag:
        await save_config(tag, sender, cmd.query("status"))
        return message("开启成功！" if cmd.query("status") else "关闭成功！").target(sender).send()


@command.parse("刷屏检测", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def check_repeat(sender: Group, cmd: Arpamar):
    await save_config(
        "mute", sender, {"time": cmd.query("time"), "mute": cmd.query("mute_time") * 60, "message": cmd.query("reply")}
    )
    message("设置成功").target(sender).send()


@command.parse("重复消息", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def duplicate(sender: Group, cmd: Arpamar):
    await save_config(
        "duplicate",
        sender,
        {"time": cmd.query("time"), "mute": cmd.query("mute_time") * 60, "message": cmd.query("reply")},
    )
    message("设置成功").target(sender).send()


@command.parse("超长消息", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def long_message(sender: Group, cmd: Arpamar):
    await save_config(
        "over-length",
        sender,
        {"len": cmd.query("len"), "mute": cmd.query("mute_time") * 60, "message": cmd.query("reply")},
    )
    message("设置成功").target(sender).send()
