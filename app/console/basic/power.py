import subprocess

from arclet.alconna import Alconna, Option, Args, Arpamar
from prompt_toolkit.styles import Style

from app.console.base import ConsoleController
from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.util.tools import restart

manager: CommandDelegateManager = CommandDelegateManager.get_instance()


@manager.register(
    entry='stop',
    brief_help='退出程序',
    many=1,
    alc=Alconna(command='stop', help_text='退出程序') + Option('--yes|-y', help_text='确认退出')
)
async def stop(self: ConsoleController, command: Arpamar):
    if command.options.get('yes'):
        await self.app.stop()
        self.console.stop()
    else:
        res: str = await self.console.prompt(
            l_prompt=[('class:warn', ' Are you sure to stop? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            await self.app.stop()
            self.console.stop()


@manager.register(
    entry='upgrade',
    brief_help='更新',
    many=2,
    alc=Alconna(command='upgrade', help_text='更新程序') + Option('--time|-t', help_text='超时时间',
                                                              args=Args['time': int:10])
)
async def upgrade(self: ConsoleController, command: Arpamar):
    try:
        shell = f'-t {Config().MASTER_QQ}'
        timeout = command.options.get('time', 10)
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


@manager.register(
    entry='reboot',
    brief_help='重启',
    many=3,
    alc=Alconna(command='reboot', help_text='重启程序') + Option('--yes|-y', help_text='确认重启')
)
async def reboot(self: ConsoleController, command: Arpamar):
    if command.options.get('yes'):
        restart('-r')
    else:
        res: str = await self.console.prompt(
            l_prompt=[('class:warn', ' Are you sure to reboot? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            restart('-r')
