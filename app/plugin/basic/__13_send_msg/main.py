from typing import Union

from arclet.alconna import AllParam

from app.core.settings import ACTIVE_GROUP
from app.util.alconna import Args, Arpamar, Commander, Option, Subcommand
from app.util.control import Permission
from app.util.graia import (
    Ariadne,
    DefaultFunctionWaiter,
    Friend,
    FriendMessage,
    Group,
    MessageChain,
    message,
)

command = Commander(
    "send",
    "主动发送消息",
    Subcommand("friend", help_text="发送好友消息", args=Args["friend_id", int]),
    Subcommand("group", help_text="发送群组消息", args=Args["group_id", int]),
    Subcommand(
        "notice",
        help_text="发送通知(这将会向所有激活的群组发送通知)",
        options=[Option("--group|-g", help_text="只对某个群发送通知", args=Args["group_id", int])],
    ),
    Option("--keep|-k", help_text="保持对话"),
    Args["msg;O", AllParam],
    help_text="主动发送消息(仅主人可用,仅限私聊)",
)


async def connect_chat(sender: Friend, target: Union[Friend, Group]):
    async def keep_chat(user: Friend, message: MessageChain):
        if user.id == sender.id:
            return message

    message(f"正在保持与{target.id}的对话，需要结束对话请发送：结束。").target(sender).send()
    while True:
        msg: MessageChain = await DefaultFunctionWaiter(keep_chat, [FriendMessage]).wait(180, "TimeoutError")
        if msg == "TimeoutError":
            message("等待超时，结束对话").target(sender).send()
            break
        elif msg.safe_display == "结束":
            message("结束对话").target(sender).send()
            break
        else:
            message(msg.as_sendable()).target(target).send()
            message("发送成功").target(sender).send()


@command.parse("friend", events=[FriendMessage], permission=Permission.MASTER)
async def send_to_friend(app: Ariadne, sender: Friend, cmd: Arpamar):
    friend_id = cmd.query("friend_id")
    if friend := await app.get_friend(friend_id):
        if cmd.find("keep"):
            await connect_chat(sender, friend)
        elif cmd.find("msg"):
            message(cmd.query("msg")).target(friend).send()
            message("发送成功").target(sender).send()
        else:
            message("缺少消息内容").target(sender).send()
    else:
        message(f"未找到好友: {friend_id}").target(sender).send()


@command.parse("group", events=[FriendMessage], permission=Permission.MASTER)
async def send_to_group(app: Ariadne, sender: Friend, cmd: Arpamar):
    group_id = cmd.query("group_id")
    if group := await app.get_group(group_id):
        if cmd.find("keep"):
            await connect_chat(sender, group)
        elif cmd.find("msg"):
            message(cmd.query("msg")).target(group).send()
            message("发送成功").target(sender).send()
        else:
            message("缺少消息内容").target(sender).send()
    else:
        message(f"未找到群组: {group_id}").target(sender).send()


@command.parse("notice", events=[FriendMessage], permission=Permission.MASTER)
async def send_notice(app: Ariadne, sender: Friend, cmd: Arpamar):
    if not cmd.find("msg"):
        return message("缺少消息内容").target(sender).send()
    msg = ("来自管理员的通知\n--------------------\n", cmd.query("msg"))
    if group_id := cmd.query("group_id"):
        if group := await app.get_group(group_id):
            message(msg).target(group).send()
        else:
            message(f"未找到群组: {group_id}").target(sender).send()
    else:
        for group_id in ACTIVE_GROUP:
            message(msg).target(await app.get_group(group_id)).send()
        message("通知发送完毕").target(sender).send()
