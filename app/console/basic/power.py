import subprocess

from arclet.alconna import Alconna, Option, Args, Arpamar
from prompt_toolkit.styles import Style

from app.console.base import ConsoleController
from app.core.command_manager import CommandManager
from app.core.config import Config
from app.util.tools import restart


class Stop(ConsoleController):
    entry = 'stop'
    brief_help = '退出程序'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(command=entry, help_text='退出程序', options=[Option('--yes', alias='-y', help_text='确认退出')]))
    async def process(self, command: Arpamar):
        if command.options:
            await self.app.stop()
            self.console.stop()
        res: str = await self.console.prompt(
            l_prompt=[('class:warn', ' Are you sure to stop? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            await self.app.stop()
            self.console.stop()


class Upgrade(ConsoleController):
    entry = 'upgrade'
    brief_help = '更新'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(command=entry, help_text='更新程序', options=[
        Option('--time', alias='-t', help_text='超时时间', args=Args['time': int:10])
    ]))
    async def process(self, command: Arpamar):
        try:
            shell = f'-t {Config().MASTER_QQ}'
            if command.options:
                timeout = command.options['time']
            else:
                timeout = 10
            try:
                ret = subprocess.call('git pull', timeout=timeout, shell=True)
                if ret == 0:
                    restart('-u', 'true', *shell)
                else:
                    return "升级失败!"
            except subprocess.TimeoutExpired:
                return "升级超时!"
        except Exception as e:
            return self.unkown_error(e)


class Reboot(ConsoleController):
    entry = 'reboot'
    brief_help = '重启'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(command=entry, help_text='重启程序', options=[Option('--yes', alias='-y', help_text='确认重启')]))
    async def process(self, command: Arpamar):
        if command.options:
            restart('-r')
        res: str = await self.console.prompt(
            l_prompt=[('class:warn', ' Are you sure to reboot? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            restart('-r')
