from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.message.parser.twilight import (
    MatchResult,
    Twilight,
    WildcardMatch
)
from loguru import logger

from app.console import *
from app.core.appCore import AppCore
from app.util.tools import parse_args, isstartswith

con: Console = AppCore.get_console(AppCore.get_core_instance())


@con.register([Twilight(['params' @ WildcardMatch()])])
async def console_handler(
        app: Ariadne,
        console: Console,
        params: MatchResult,
):
    if param := params.result.asDisplay():
        send_help = False  # 是否为主菜单帮助
        resp = 'Usage: [COMMAND] [OPTION]'
        param = parse_args(param, keep_head=True)
        # 判断是否为主菜单帮助
        if isstartswith(param[0], 'help', full_match=True):
            send_help = True

        for func in base.ConsoleController.__subclasses__():
            obj = func(params, console, app)
            if send_help:
                resp += f"\n\t{format(obj.entry, '<30')}\t{obj.brief_help}"
            elif isstartswith(param[0], obj.entry, full_match=True):
                resp = await obj.get_resp()
                await _do_send(resp)
                return

        # 主菜单帮助发送
        if send_help:
            await _do_send(resp)
        else:
            await _do_send('command not found: ' + param[0])


async def _do_send(resp):
    """回送消息"""
    logger.opt(raw=True).info((resp or '').strip('\n') + '\n\n' if resp else '\n')


logger.success("控制台监听器启动成功")
