from typing import Union

from app.util.alconna import Args, Arpamar, Commander, Option
from app.util.control import Permission
from app.util.graia import Friend, Group, GroupMessage, Plain, message
from app.util.online_config import save_config

configs = {"禁言退群": "bot_mute_event", "上线通知": "online_notice"}
command = Commander(
    "sys",
    "系统",
    Option("禁言退群", help_text="设置机器人禁言是否退群", args=Args["bool", bool]),
    Option("上线通知", help_text="设置机器人上线是否通知该群", args=Args["bool", bool]),
    help_text="系统设置: 仅主人可用!",
    hidden=True,
)


@command.parse(["禁言退群", "上线通知"], events=[GroupMessage], permission=Permission.MASTER)
async def process(sender: Union[Friend, Group], cmd: Arpamar):
    await save_config(configs[list(cmd.options.keys())[0]], sender.id, cmd.query("bool"))
    return message([Plain("开启成功！" if cmd.query("bool") else "关闭成功！")]).target(sender).send()
