import subprocess

from arclet.alconna import Alconna, Args, Arpamar, CommandMeta, Option
from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne.console import Console
from prompt_toolkit.styles import Style

from app.console.util import send, unknown_error
from app.core.app import AppCore
from app.core.config import Config

core: AppCore = AppCore()
con: Console = core.get_console()
alc_stop = Alconna("stop", meta=CommandMeta("退出程序")) + Option("--yes|-y", help_text="确认退出")


@con.register([AlconnaDispatcher(alc_stop)])
async def stop(console: Console, cmd: Arpamar):
    if not cmd.matched:
        return send(alc_stop.help_text)
    if cmd.options.get("yes"):
        core.stop()
    else:
        res: str = await console.prompt(
            l_prompt=[("class:warn", " Are you sure to stop? "), ("", " (y/n) ")],
            style=Style([("warn", "bg:#cccccc fg:#d00000")]),
        )
        if res.lower() in ("y", "yes"):
            core.stop()


alc_upgrade = Alconna("upgrade", meta=CommandMeta("更新程序")) + Option(
    "--time|-t", help_text="超时时间", args=Args["time", int, 10]
)


@con.register([AlconnaDispatcher(alc_upgrade)])
async def upgrade(cmd: Arpamar):
    if not cmd.matched:
        return send(alc_upgrade.help_text)
    try:
        shell = f"-t {Config.master_qq}"
        timeout = cmd.options.get("time", 10)
        try:
            ret = subprocess.call("git pull", timeout=timeout, shell=True)
            if ret == 0:
                core.restart("-u", "true", *shell)
            else:
                return send("升级失败!")
        except subprocess.TimeoutExpired:
            return send("升级超时!")
    except Exception as e:
        return unknown_error(e)


alc_reboot = Alconna("reboot", meta=CommandMeta("重启程序")) + Option("--yes|-y", help_text="确认重启")


@con.register([AlconnaDispatcher(alc_reboot)])
async def reboot(console: Console, cmd: Arpamar):
    if not cmd.matched:
        return send(alc_reboot.help_text)
    if cmd.options.get("yes"):
        core.restart("-r")
    else:
        res: str = await console.prompt(
            l_prompt=[("class:warn", " Are you sure to reboot? "), ("", " (y/n) ")],
            style=Style([("warn", "bg:#cccccc fg:#d00000")]),
        )
        if res.lower() in ("y", "yes"):
            core.restart("-r")
