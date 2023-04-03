import asyncio
from datetime import datetime

from dateutil.relativedelta import relativedelta
from graia.ariadne.event.mirai import (
    BotGroupPermissionChangeEvent,
    BotInvitedJoinGroupRequestEvent,
    BotJoinGroupEvent,
    BotLeaveEventActive,
    BotLeaveEventKick,
    BotMuteEvent,
    NudgeEvent,
)
from loguru import logger

from app.core.app import AppCore
from app.core.config import Config
from app.core.settings import ACTIVE_GROUP, ADMIN_USER, NUDGE_INFO
from app.entities.group import BotGroup
from app.util.graia import (
    Ariadne,
    Friend,
    FriendMessage,
    FunctionWaiter,
    MessageChain,
    Plain,
    message,
)
from app.util.online_config import get_config

core: AppCore = AppCore()
bcc = core.get_bcc()


@bcc.receiver(BotInvitedJoinGroupRequestEvent)
async def invited_join_group_request(event: BotInvitedJoinGroupRequestEvent):
    """被邀请入群"""
    if event.source_group in ACTIVE_GROUP:
        message(
            [
                Plain("收到邀请入群事件"),
                Plain(f"\r\n邀请者: {event.supplicant} | {event.nickname}"),
                Plain(f"\r\n群号: {event.source_group}"),
                Plain(f"\r\n群名: {event.group_name}"),
                Plain("\r\n该群为白名单群，已同意加入"),
            ]
        ).target(Config.master_qq).send()
        await event.accept()
    else:
        message(
            [
                Plain("收到邀请入群事件"),
                Plain(f"\r\n邀请者: {event.supplicant} | {event.nickname}"),
                Plain(f"\r\n群号: {event.source_group}"),
                Plain(f"\r\n群名: {event.group_name}"),
                Plain("\n\n请发送“同意”或“拒绝”"),
            ]
        ).target(Config.master_qq).send()

        async def waiter(waiter_friend: Friend, waiter_message: MessageChain):
            if waiter_friend.id == Config.master_qq:
                saying = waiter_message.display
                if saying == "同意":
                    return True
                elif saying == "拒绝":
                    return False
                else:
                    message("请发送同意或拒绝").target(Config.master_qq).send()

        try:
            if await FunctionWaiter(waiter, [FriendMessage]).wait(300):
                if event.source_group not in ACTIVE_GROUP:
                    BotGroup(event.source_group, active=1)
                    ACTIVE_GROUP.update({event.source_group: "*"})
                await event.accept()
                message("已同意申请并加入白名单").target(Config.master_qq).send()
            else:
                await event.reject("主人拒绝加入该群")
                message("已拒绝申请").target(Config.master_qq).send()

        except asyncio.TimeoutError:
            await event.reject("由于主人长时间未审核，已自动拒绝")
            message("申请超时已自动拒绝").target(Config.master_qq).send()


@bcc.receiver(BotJoinGroupEvent)
async def join_group(app: Ariadne, event: BotJoinGroupEvent):
    """收到入群事件"""
    member_num = len(await app.get_member_list(event.group))
    message(
        [
            Plain("收到加入群聊事件"),
            Plain(f"\n群号：{event.group.id}"),
            Plain(f"\n群名：{event.group.name}"),
            Plain(f"\n群人数：{member_num}"),
        ]
    ).target(Config.master_qq).send()
    if event.group.id not in ACTIVE_GROUP:
        await message(f"该群未在白名单中，正在退出，如有需要请联系{Config.master_qq}申请白名单").target(
            event.group
        ).immediately_send()  # noqa: E501
        message("该群未在白名单中，正在退出").target(Config.master_qq).send()
        return await app.quit_group(event.group.id)

    message(
        f"我是{Config.master_name}"
        f"的机器人{Config.name}，"
        f"如果有需要可以联系主人QQ“{Config.master_qq}”，"
        f"添加{Config.name}好友后请私聊说明用途后即可拉进其他群，主人看到后会选择是否同意入群"
        f"\n{Config.name}被群禁言后会自动退出该群。"
        "\n发送 <.help> 可以查看功能列表"
        "\n拥有管理员以上权限可以开关功能"
        f"\n注：@{Config.name}可以触发聊天功能"
    ).target(event.group).send()


@bcc.receiver(BotLeaveEventKick)
async def leave_kick(event: BotLeaveEventKick):
    """被踢出群"""
    try:
        await BotGroup(event.group.id, 0).group_deactivate()
        ACTIVE_GROUP.pop(event.group.id)
    except Exception as e:
        logger.warning(e)
    for qq in ADMIN_USER:
        message(
            "收到被踢出群聊事件",
            f"\n群号: {event.group.id}",
            f"\n群名: {event.group.name}",
            "\n已移出白名单",
        ).target(qq).send()


@bcc.receiver(BotLeaveEventActive)
async def leave_active(event: BotLeaveEventActive):
    """主动退群"""
    try:
        await BotGroup(event.group.id, 0).group_deactivate()
        ACTIVE_GROUP.pop(event.group.id)
    except Exception as e:
        logger.warning(e)
    for qq in ADMIN_USER:
        message(
            "收到主动退出群聊事件",
            f"\n群号: {event.group.id}",
            f"\r\n群名: {event.group.name}",
            "\r\n已移出白名单",
        ).target(qq).send()


@bcc.receiver(BotGroupPermissionChangeEvent)
async def group_permission_change(app: Ariadne, event: BotGroupPermissionChangeEvent):
    """群内权限变动"""
    for qq in ADMIN_USER:
        message(
            [
                Plain("收到权限变动事件"),
                Plain(f"\r\n群号: {event.group.id}"),
                Plain(f"\r\n群名: {event.group.name}"),
                Plain(f"\r\n权限变更为: {event.current}"),
            ]
        ).target(qq).send()


@bcc.receiver(BotMuteEvent)
async def mute(app: Ariadne, event: BotMuteEvent):
    """被禁言"""
    res = await get_config("bot_mute_event", event.operator.group.id)
    if res is None or res:
        try:
            await BotGroup(event.operator.group.id, 0).group_deactivate()
            ACTIVE_GROUP.pop(event.operator.group.id)
        except Exception as e:
            logger.warning(e)

        for qq in ADMIN_USER:
            message(
                [
                    Plain("收到禁言事件， 已退出该群，并移出白名单"),
                    Plain(f"\r\n群号: {event.operator.group.id}"),
                    Plain(f"\r\n群名: {event.operator.group.id}"),
                    Plain(f"\r\n操作者: {event.operator.name} | {event.operator.id}"),
                ]
            ).target(qq).send()
        await app.quit_group(event.operator.group)


@bcc.receiver(NudgeEvent)
async def nudge(app: Ariadne, event: NudgeEvent):
    """被戳一戳"""
    if event.target != Config.bot.account:
        return
    if event.context_type == "group":
        if member := await app.get_member(event.group_id, event.supplicant):
            logger.info(f"机器人被群 <{member.group.name}> 中用户 <{member.name}> 戳了戳。")
            if member.group.id in NUDGE_INFO.keys():
                if member.id in NUDGE_INFO[member.group.id].keys():
                    period = NUDGE_INFO[member.group.id][member.id]["time"] + relativedelta(minutes=1)
                    if datetime.now() >= period:
                        NUDGE_INFO[member.group.id][member.id] = {
                            "count": 0,
                            "time": datetime.now(),
                        }
                    count = NUDGE_INFO[member.group.id][member.id]["count"] + 1
                    if count == 1:
                        try:
                            await app.send_nudge(member)
                        except Exception as e:
                            logger.warning(e)
                        NUDGE_INFO[member.group.id][member.id] = {
                            "count": count,
                            "time": datetime.now(),
                        }
                    elif count == 2:
                        try:
                            message(" 不许戳了！").at(member).target(member.group).send()
                            await app.send_nudge(member)
                        except Exception as e:
                            logger.warning(e)
                        NUDGE_INFO[member.group.id][member.id] = {
                            "count": count,
                            "time": datetime.now(),
                        }
                    elif count == 3:
                        try:
                            message(" 说了不许再戳了！").at(member).target(member.group).send()
                            await app.send_nudge(member)
                        except Exception as e:
                            logger.warning(e)
                        NUDGE_INFO[member.group.id][member.id] = {
                            "count": count,
                            "time": datetime.now(),
                        }
                    elif count == 4:
                        try:
                            await app.send_nudge(member)
                        except Exception as e:
                            logger.warning(e)
                        NUDGE_INFO[member.group.id][member.id] = {
                            "count": count,
                            "time": datetime.now(),
                        }
                    elif count == 5:
                        try:
                            message(" 呜呜呜你欺负我，不理你了！").at(member).target(member.group).send()
                            await app.send_nudge(member)
                        except Exception as e:
                            logger.warning(e)
                        NUDGE_INFO[member.group.id][member.id] = {
                            "count": count,
                            "time": datetime.now(),
                        }
                    elif 6 <= count <= 9:
                        NUDGE_INFO[member.group.id][member.id] = {
                            "count": count,
                            "time": datetime.now(),
                        }
                    elif count == 10:
                        try:
                            message(" 你真的很有耐心诶。").at(member).target(member.group).send()
                            await app.send_nudge(member)
                        except Exception as e:
                            logger.warning(e)
                else:
                    NUDGE_INFO[member.group.id][member.id] = {
                        "count": 1,
                        "time": datetime.now(),
                    }
                    await app.send_nudge(member)
            else:
                NUDGE_INFO[member.group.id] = {member.id: {"count": 1, "time": datetime.now()}}
                await app.send_nudge(member)
    elif friend := await app.get_friend(event.supplicant):
        logger.info(f"机器人被好友 <{friend.nickname}> 戳了戳。")
