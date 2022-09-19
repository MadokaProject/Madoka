from typing import Union

from arclet.alconna import Alconna, Args, Arpamar, CommandMeta, Option, Subcommand
from graia.ariadne import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Source
from graia.ariadne.model import Friend, Group, Member
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.util.control import Permission
from app.util.online_config import save_config
from app.util.phrases import (
    args_error,
    exec_permission_error,
    print_help,
    unknown_error,
)

manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry="csm",
    brief_help="群管",
    alc=Alconna(
        "csm",
        Subcommand(
            "mute",
            args=Args["at", At, ...],
            help_text="禁言指定群成员",
            options=[
                Option("--time|-t", args=Args["time", int, 10], help_text="禁言时间(分)"),
                Option("--all|-a", help_text="开启全员禁言"),
            ],
        ),
        Subcommand(
            "unmute", args=Args["at", At, ...], help_text="取消禁言指定群成员", options=[Option("--all|-a", help_text="关闭全员禁言")]
        ),
        Subcommand(
            "func",
            args=Args["status", bool],
            help_text="功能开关",
            options=[
                Option("--card|-C", help_text="成员名片修改通知"),
                Option("--flash|-F", help_text="闪照识别"),
                Option("--recall|-R", help_text="撤回识别"),
                Option("--kick|-K", help_text="成员被踢通知"),
                Option("--quit|-Q", help_text="成员退群通知"),
            ],
        ),
        Option("status", args=Args["status", bool], help_text="开关群管"),
        Option("kick", args=Args["at", At], help_text="踢出指定群成员"),
        Option("revoke", args=Args["id", int], help_text="撤回消息, id=消息ID, 自最后一条消息起算"),
        Option(
            "刷屏检测",
            args=Args["time", int]["mute_time", int]["reply", str],
            help_text="检测time内的3条消息是否刷屏; time: 秒, mute_time: 分钟, reply: 回复消息",
        ),
        Option(
            "重复消息",
            args=Args["time", int]["mute_time", int]["reply", str],
            help_text="检测time内的3条消息是否重复; time: 秒, mute_time: 分钟, reply: 回复消息",
        ),
        Option(
            "超长消息",
            args=Args["len", int]["mute_time", int]["reply", str],
            help_text="检测单消息是否超出设定的长度; len: 文本长度, mute_time: 分钟, reply: 回复消息",
        ),
        meta=CommandMeta("群管助手"),
    ),
)
@Permission.require(level=Permission.GROUP_ADMIN)
async def process(
    app: Ariadne,
    sender: Union[Friend, Group],
    source: Source,
    command: Arpamar,
    alc: Alconna,
    _: Union[Friend, Member],
):
    components = command.options.copy()
    components.update(command.subcommands)
    if not components:
        return await print_help(alc.get_help())
    try:
        if not isinstance(sender, Group):
            return MessageChain([Plain("请在群聊内使用该命令!")])
        if status := components.get("status"):
            await save_config("status", sender.id, status["status"])
            return MessageChain([Plain("开启成功!" if status["status"] else "关闭成功!")])
        elif kick := components.get("kick"):
            await app.kick_member(sender, kick["at"].target)
            return MessageChain([Plain("飞机票快递成功!")])
        elif revoke := components.get("revoke"):
            await app.recall_message(source.id - revoke["id"])
            return MessageChain([Plain("消息撤回成功!")])
        elif mute := components.get("mute"):
            if mute.get("all"):
                await app.mute_all(sender.id)
                return MessageChain([Plain("开启全员禁言成功!")])
            elif target := mute.get("at"):
                time = mute["time"]["time"] if mute.get("time") else 10
                await app.mute_member(sender, target.target, time * 60)
                return MessageChain([Plain("禁言成功!")])
        elif unmute := components.get("unmute"):
            if unmute.get("all"):
                await app.unmute_all(sender)
                return MessageChain([Plain("关闭全员禁言成功!")])
            elif target := unmute.get("at"):
                await app.unmute_member(sender, target.target)
                return MessageChain([Plain("解除禁言成功!")])
        elif func := components.get("func"):
            tag = None
            if func.get("card"):
                tag = "member_card_change"
            elif func.get("quit"):
                tag = "member_quit"
            elif func.get("kick"):
                tag = "member_kick"
            elif func.get("flash"):
                tag = "flash_png"
            elif func.get("recall"):
                tag = "member_recall"
            if tag:
                await save_config(tag, sender, func["status"])
                return MessageChain([Plain("开启成功！" if func["status"] else "关闭成功！")])
        elif repeat := components.get("刷屏检测"):
            await save_config(
                "mute",
                sender,
                {
                    "time": repeat["time"],
                    "mute": repeat["mute_time"] * 60,
                    "message": repeat["reply"],
                },
            )
            return MessageChain([Plain("设置成功!")])
        elif duplicate := components.get("重复消息"):
            await save_config(
                "duplicate",
                sender,
                {
                    "time": duplicate["time"],
                    "mute": duplicate["mute_time"] * 60,
                    "message": duplicate["reply"],
                },
            )
            return MessageChain([Plain("设置成功!")])
        elif too_long := components.get("超长消息"):
            await save_config(
                "over-length",
                sender,
                {
                    "text": too_long["len"],
                    "mute": too_long["mute_time"] * 60,
                    "message": too_long["reply"],
                },
            )
            return MessageChain([Plain("设置成功!")])
        return args_error()
    except PermissionError:
        return exec_permission_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()
