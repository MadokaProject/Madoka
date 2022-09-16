from arclet.alconna import Alconna, command_manager
from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne.console import Console

from app.console.util import send
from app.core.app import AppCore

con: Console = AppCore().get_console()


@con.register([AlconnaDispatcher(Alconna(command="help", help_text="查看帮助信息"))])
async def process():
    send(command_manager.all_command_help(namespace="Alconna"))
