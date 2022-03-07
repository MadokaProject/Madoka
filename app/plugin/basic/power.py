import subprocess

from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.console import Console
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from loguru import logger

from app.core.appCore import AppCore
from app.core.command_manager import CommandManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.tools import restart


class Module(Plugin):
    entry = 'p'
    brief_help = '电源'
    hidden = True
    manager: CommandManager = CommandManager.get_command_instance()

    @permission_required(level=Permission.MASTER)
    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('k', help_text='关闭机器人'),
            Subcommand('r', help_text='重启机器人'),
            Subcommand('u', help_text='升级机器人', options=[
                Option('--timeout', alias='-t', args=Args['timeout': int: 10])
            ])
        ],
        help_text='电源控制, 仅主人可用'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        other_args = command.other_args
        if not subcommand:
            return await self.print_help(alc.get_help())
        try:
            if subcommand:
                shell = ''
                con: Console = AppCore.get_console(AppCore.get_core_instance())
                if hasattr(self, 'group'):
                    shell = [f'-g {self.group.id}', f'-t {self.member.id}']
                elif hasattr(self, 'friend'):
                    shell = f'-t {self.friend.id}'
                if subcommand.__contains__('u'):
                    timeout = 10
                    if other_args.__contains__('timeout') and other_args['timeout'] > 0:
                        timeout = other_args['timeout']
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
                elif subcommand.__contains__('r'):
                    con.stop()
                    restart('-r', *shell)
                await self.app.stop()
                con.stop()
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()
