from arclet.alconna import Alconna, Args, Arpamar, Option, exclusion
from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne import Ariadne
from graia.ariadne.console import Console

from app.console.util import args_error, exec_permission_error, send, unknown_error
from app.core.app import AppCore

con: Console = AppCore().get_console()
alc = Alconna(
    command="csm",
    options=[
        Option(
            "mute",
            help_text="禁言指定群成员",
            args=Args["group", int]["qq", int, 0]["time", int, 10],
        ),
        Option(
            "unmute",
            help_text="解除禁言指定群成员",
            args=Args["group", int]["qq", int, 0],
        ),
        Option("--all|-a", help_text="是否作用于全员"),
    ],
    help_text="群管助手",
    behaviors=[exclusion("options.mute", "options.unmute")],
)


@con.register([AlconnaDispatcher(alc)])
async def process(app: Ariadne, cmd: Arpamar):
    if not cmd.matched:
        return send(alc.help_text)
    other_args = cmd.other_args
    all_ = True if cmd.options.get("all") else False
    if not cmd.options.get("mute") and not cmd.options.get("unmute"):
        return args_error()
    qq = other_args["qq"]
    if not all_ and qq <= 0:
        return args_error()
    if (grp := (await app.get_group(other_args["group"]))) is None:
        return send("未找到该群组")
    if (mbr := (await app.get_member(grp, qq))) is None and not all_:
        return send("未找到该成员")
    try:
        if cmd.options.get("mute"):
            if all_:
                await app.mute_all(grp)
                return send("全员禁言成功!")
            await app.mute_member(grp, mbr, other_args["time"] * 60)
            return send("禁言成功!")
        elif cmd.options.get("unmute"):
            if all_:
                await app.unmute_all(grp)
                return send("取消全员禁言成功!")
            await app.unmute_member(grp, mbr)
            return send("解除禁言成功!")
        else:
            return args_error()
    except PermissionError:
        return exec_permission_error()
    except Exception as e:
        return unknown_error(e)
