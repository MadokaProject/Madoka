import subprocess

from arclet.alconna import Alconna, Option, Args
from arclet.alconna.graia import AlconnaDispatcher, AlconnaProperty
from graia.ariadne import Ariadne
from graia.ariadne.console import Console
from prompt_toolkit.styles import Style

from app.console.util import *
from app.core.app import AppCore
from app.core.config import Config
from app.util.tools import restart

con: Console = AppCore.get_core_instance().get_console()


@con.register([AlconnaDispatcher(
    Alconna(command='stop', help_text='退出程序') + Option('--yes|-y', help_text='确认退出')
)])
async def stop(app: Ariadne, console: Console, result: AlconnaProperty):
    arp = result.result
    if not arp.matched:
        return send(result.help_text)
    if arp.options.get('yes'):
        app.stop()
        console.stop()
    else:
        res: str = await console.prompt(
            l_prompt=[('class:warn', ' Are you sure to stop? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            app.stop()
            console.stop()


@con.register([AlconnaDispatcher(
    Alconna(command='upgrade', help_text='更新程序') + Option('--time|-t', help_text='超时时间', args=Args['time', int, 10])
)])
async def upgrade(result: AlconnaProperty):
    arp = result.result
    if not arp.matched:
        return send(result.help_text)
    try:
        shell = f'-t {Config().MASTER_QQ}'
        timeout = arp.options.get('time', 10)
        try:
            ret = subprocess.call('git pull', timeout=timeout, shell=True)
            if ret == 0:
                restart('-u', 'true', *shell)
            else:
                return send("升级失败!")
        except subprocess.TimeoutExpired:
            return send("升级超时!")
    except Exception as e:
        return unknown_error(e)


@con.register([AlconnaDispatcher(
    Alconna(command='reboot', help_text='重启程序') + Option('--yes|-y', help_text='确认重启')
)])
async def reboot(console: Console, result: AlconnaProperty):
    arp = result.result
    if not arp.matched:
        return send(result.help_text)
    if arp.options.get('yes'):
        restart('-r')
    else:
        res: str = await console.prompt(
            l_prompt=[('class:warn', ' Are you sure to reboot? '), ('', ' (y/n) ')],
            style=Style([('warn', 'bg:#cccccc fg:#d00000')]),
        )
        if res.lower() in ('y', 'yes'):
            restart('-r')
