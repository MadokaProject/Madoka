import subprocess
from typing import Union

from loguru import logger

from app.core.app import AppCore
from app.util.alconna import Args, Arpamar, Commander, Option, Subcommand
from app.util.control import Permission
from app.util.graia import Friend, Group, Member, message

core: AppCore = AppCore()
command = Commander(
    "p",
    "电源",
    Subcommand("u", help_text="升级机器人", options=[Option("--timeout|-t", args=Args["timeout", int, 10])]),
    Option("k", help_text="关闭机器人"),
    Option("r", help_text="重启机器人"),
    help_text="电源控制, 仅主人可用",
    hidden=True,
)


def shell(target: Union[Friend, Member], sender: Union[Friend, Group]):
    if isinstance(sender, Group):
        return [f"-g {sender.id}", f"-t {target.id}"]
    else:
        return f"-t {sender.id}"


@command.parse("u", permission=Permission.MASTER)
async def update(target: Union[Friend, Member], sender: Union[Friend, Group], cmd: Arpamar):
    timeout = cmd.query("timeout") or 10
    try:
        ret = subprocess.call("git pull", timeout=timeout, shell=True)
        if ret == 0:
            core.restart("-u", "true", *shell(target, sender))
        else:
            core.restart("-u", "false", *shell(target, sender))
    except subprocess.TimeoutExpired:
        logger.warning("升级超时！")
        msg = message(" 升级超时！").target(sender)
        if isinstance(sender, Group):
            msg.at(target).send()
        else:
            msg.send()


@command.parse("r", permission=Permission.MASTER)
async def restart(target: Union[Friend, Member], sender: Union[Friend, Group]):
    core.restart(*shell(target, sender))


@command.parse("k", permission=Permission.MASTER)
async def kill():
    core.stop()
