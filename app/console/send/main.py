from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne.console import Console

from app.console.util import send
from app.core.app import AppCore
from app.util.alconna import Alconna, Args, Arpamar, CommandMeta, Option
from app.util.graia import Ariadne, message

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
    message(cmd.query("msg")).target(cmd.query("num")).send()
