from prompt_toolkit.styles import Style

from app.console.base import ConsoleController
from app.util.tools import restart


class Stop(ConsoleController):
    entry = 'stop'
    brief_help = '退出程序'
    full_help = {
        'stop': '停止并退出Madoka'
    }

    async def process(self):
        if self.param:
            self.print_help()
            return
        res: str = await self.console.prompt(
            l_prompt=[('class:warn', ' Are you sure to stop? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            await self.app.stop()
            self.console.stop()


class Reboot(ConsoleController):
    entry = 'reboot'
    brief_help = '重启'
    full_help = {
        'reboot': '停止并重启Madoka'
    }

    async def process(self):
        res: str = await self.console.prompt(
            l_prompt=[('class:warn', ' Are you sure to reboot? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            restart('-r')
