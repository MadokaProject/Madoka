import subprocess

from prompt_toolkit.styles import Style

from app.console.base import ConsoleController
from app.core.config import Config
from app.util.tools import restart, isstartswith


class Stop(ConsoleController):
    entry = 'stop'
    brief_help = '退出程序'
    full_help = {}

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


class Upgrade(ConsoleController):
    entry = 'upgrade'
    brief_help = '更新'
    full_help = {
        '-t, --time': '超时时间[Default: 10s]'
    }

    async def process(self):
        try:
            shell = f'-t {Config().MASTER_QQ}'
            if len(self.param) >= 1:
                assert isstartswith(self.param[0], ['-t', '--time'])
                if not self.param[1].isdigit():
                    raise KeyError
                timeout = int(self.param[1])
            else:
                timeout = 10
            try:
                ret = subprocess.call('git pull', timeout=timeout, shell=True)
                if ret == 0:
                    restart('-u', 'true', *shell)
                else:
                    self.resp = "升级失败!"
            except subprocess.TimeoutExpired:
                self.resp = "升级超时!"
        except AssertionError:
            self.args_error()
        except KeyError:
            self.arg_type_error()
        except Exception as e:
            self.unkown_error(e)


class Reboot(ConsoleController):
    entry = 'reboot'
    brief_help = '重启'
    full_help = {}

    async def process(self):
        res: str = await self.console.prompt(
            l_prompt=[('class:warn', ' Are you sure to reboot? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            restart('-r')
