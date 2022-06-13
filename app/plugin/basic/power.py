import subprocess

from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.console import Console
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from loguru import logger

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.tools import restart

manager: CommandDelegateManager = CommandDelegateManager.get_instance()


@permission_required(level=Permission.MASTER)
@manager.register(
    entry='p',
    brief_help='电源',
    hidden=True,
    alc=Alconna(
        headers=manager.headers,
        command='p',
        options=[
            Subcommand('u', help_text='升级机器人', options=[
                Option('--timeout|-t', args=Args['timeout': int: 10])
            ]),
            Option('k', help_text='关闭机器人'),
            Option('r', help_text='重启机器人'),
        ],
        help_text='电源控制, 仅主人可用'
    )
)
async def process(self: Plugin, command: Arpamar, alc: Alconna):
    components = command.options.copy()
    components.update(command.subcommands)
    if not components:
        return await self.print_help(alc.get_help())
    try:
        shell = ''
        con: Console = AppCore.get_console(AppCore.get_core_instance())
        if hasattr(self, 'group'):
            shell = [f'-g {self.group.id}', f'-t {self.member.id}']
        elif hasattr(self, 'friend'):
            shell = f'-t {self.friend.id}'
        if 'u' in components:
            u = components['u']
            timeout = u['timeout']['timeout'] if command.find('timeout') else 10
            try:
                ret = subprocess.call('git pull', timeout=timeout, shell=True)
                con.stop()
                if ret == 0:
                    restart('-u', 'true', *shell)
                else:
                    restart('-u', 'false', *shell)
            except subprocess.TimeoutExpired:
                logger.warning('升级超时！')
                if hasattr(self, 'group'):
                    return MessageChain.create([At(self.member.id), Plain(" 升级超时！")])
                else:
                    return MessageChain.create([Plain("升级超时！")])
        elif 'r' in components:
            con.stop()
            restart('-r', *shell)
        elif 'k' in components:
            con.stop()
            await self.app.stop()
        else:
            return self.args_error()
    except Exception as e:
        logger.exception(e)
        return self.unkown_error()
