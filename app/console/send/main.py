from arclet.alconna import Alconna, Args, Arpamar, CommandMeta, Option
from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.console.util import args_error, send
from app.core.app import AppCore

con: Console = AppCore().get_console()
alc = Alconna(
    "send",
    Args["msg", str],
    Option("--friend|-f", help_text="向指定好友发送消息", args=Args["num", int]),
    Option("--group|-g", help_text="向指定群组发送消息", args=Args["num", int]),
    meta=CommandMeta("发送消息"),
)


@con.register([AlconnaDispatcher(alc)])
async def process(app: Ariadne, cmd: Arpamar):
    if not cmd.matched:
        return send(alc.help_text)
    if frd := cmd.options.get("friend"):
        if await app.get_friend(frd["num"]):
            await app.send_friend_message(frd["num"], MessageChain(Plain(cmd.query("msg"))))
            return send("发送成功!")
        return send("未找到该好友")
    elif gp := cmd.options.get("group"):
        if await app.get_group(gp["num"]):
            await app.send_group_message(gp["num"], MessageChain(Plain(cmd.query("msg"))))
            return send("发送成功!")
        return send("未找到该群组")
    return args_error()
