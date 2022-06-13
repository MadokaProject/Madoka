import sys

from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.message.parser.twilight import (
    MatchResult,
    Twilight,
    WildcardMatch
)
from loguru import logger

from app.console.base import ConsoleController
from app.core.appCore import AppCore
from app.util.tools import parse_args, isstartswith, Autonomy

core: AppCore = AppCore.get_core_instance()
con: Console = core.get_console()
manager = core.get_manager()


@con.register([Twilight(['params' @ WildcardMatch()])])
async def console_handler(
        app: Ariadne,
        console: Console,
        params: MatchResult,
):
    if params := params.result.asDisplay():
        send_help = False  # 是否为主菜单帮助
        resp = 'Usage: [COMMAND] [OPTION]'
        param = parse_args(params, keep_head=True)
        # 判断是否为主菜单帮助
        if isstartswith(param[0], 'help', full_match=True):
            send_help = True

        for plg in manager.get_delegates('console').values():
            if send_help:
                resp += f"\n\t{format(plg.entry, '<30')}\t{plg.brief_help}"
            elif isstartswith(param[0], plg.entry, full_match=True):
                current = sys.stdout
                alc_help = Autonomy()
                sys.stdout = alc_help
                try:
                    result = plg.alc.parse(params)
                    if result.matched:
                        sys.stdout = current
                        resp = await plg.func(
                            ConsoleController(params, console, app),
                            result
                        )
                    elif result.head_matched:
                        if alc_help.buff:
                            resp = alc_help.buff
                        else:
                            resp = '参数错误!'
                        sys.stdout = current
                except Exception as e:
                    resp = str(e)
                sys.stdout = current
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
