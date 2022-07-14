import subprocess
from typing import Union

from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.message.element import At
from graia.ariadne.model import Friend, Member, Group
from loguru import logger

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.util.control import Permission
from app.util.phrases import *
from app.util.tools import restart

core: AppCore = AppCore()
app: Ariadne = core.get_app()
con: Console = core.get_console()
manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry='p',
    brief_help='电源',
    hidden=True,
    alc=Alconna(
        headers=manager.headers,
        command='p',
        options=[
            Subcommand('u', help_text='升级机器人', options=[
                Option('--timeout|-t', args=Args['timeout', int, 10])
            ]),
            Option('k', help_text='关闭机器人'),
            Option('r', help_text='重启机器人'),
        ],
        help_text='电源控制, 仅主人可用'
    )
)
@Permission.require(level=Permission.MASTER)
async def process(target: Union[Friend, Member], sender: Union[Friend, Group], cmd: Arpamar, alc: Alconna):
    if not cmd.components:
        return await print_help(alc.get_help())
    try:
        if isinstance(sender, Group):
            shell = [f'-g {sender.id}', f'-t {target.id}']
        else:
            shell = f'-t {sender.id}'
        if cmd.find('u'):
            timeout = cmd.query('timeout') or 10
            try:
                ret = subprocess.call('git pull', timeout=timeout, shell=True)
                con.stop()
                if ret == 0:
                    restart('-u', 'true', *shell)
                else:
                    restart('-u', 'false', *shell)
            except subprocess.TimeoutExpired:
                logger.warning('升级超时！')
                if isinstance(sender, Group):
                    return MessageChain([At(target.id), Plain(" 升级超时！")])
                else:
                    return MessageChain([Plain("升级超时！")])
        elif cmd.find('r'):
            con.stop()
            restart('-r', *shell)
        elif cmd.find('k'):
            con.stop()
            app.stop()
        else:
            return args_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()
