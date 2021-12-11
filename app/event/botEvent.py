import asyncio
import time

from datetime import datetime
from dateutil.relativedelta import relativedelta
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend
from graia.broadcast.interrupt.waiter import Waiter
from loguru import logger

from app.core.config import Config
from app.core.settings import NUDGE_INFO
from app.core.settings import ACTIVE_GROUP, ADMIN_USER
from app.entities.group import BotGroup
from app.event.base import Event
from app.util.control import Rest
from app.util.dao import MysqlDao
from app.util.sendMessage import safeSendGroupMessage


class BotInit(Event):
    """PyIBot 成功启动"""
    event_name = "ApplicationLaunched"

    async def process(self):
        config = Config()
        groupList = await self.app.getGroupList()
        groupNum = len(groupList)
        await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
            Plain('PyIBot 成功启动。\r\n'),
            Plain(f'当前 {config.BOT_NAME} 共加入了 {groupNum} 个群')
        ]))
        now_localtime = time.strftime("%H:%M:%S", time.localtime())
        if "00:00:00" < now_localtime < "07:30:00":
            Rest.set_sleep(1)
            await self.app.sendFriendMessage(
                config.MASTER_QQ,
                MessageChain.create([Plain("夜深了，早点休息")]),
            )


class BotStop(Event):
    """PyIBot 关闭"""
    event_name = "ApplicationShutdowned"

    async def process(self):
        config = Config()
        await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([Plain('正在关闭')]))


class BotInvitedJoinGroupRequest(Event):
    """被邀请入群"""
    event_name = "BotInvitedJoinGroupRequestEvent"

    async def process(self):
        config = Config()
        if self.bot_invited_join.groupId in ACTIVE_GROUP:
            await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
                Plain("收到邀请入群事件"),
                Plain(f"\r\n邀请者: {self.bot_invited_join.supplicant} | {self.bot_invited_join.nickname}"),
                Plain(f"\r\n群号: {self.bot_invited_join.groupId}"),
                Plain(f"\r\n群名: {self.bot_invited_join.groupName}"),
                Plain(f"\r\n该群为白名单群，已同意加入")
            ]))
            await self.bot_invited_join.accept()
        else:
            await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
                Plain("收到邀请入群事件"),
                Plain(f"\r\n邀请者: {self.bot_invited_join.supplicant} | {self.bot_invited_join.nickname}"),
                Plain(f"\r\n群号: {self.bot_invited_join.groupId}"),
                Plain(f"\r\n群名: {self.bot_invited_join.groupName}"),
                Plain(f"\n\n请发送“同意”或“拒绝”")
            ]))

            @Waiter.create_using_function([FriendMessage])
            async def waiter(waiter_friend: Friend, waiter_message: MessageChain):
                if waiter_friend.id == config.MASTER_QQ:
                    saying = waiter_message.asDisplay()
                    if saying == "同意":
                        return True
                    elif saying == "拒绝":
                        return False
                    else:
                        await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
                            Plain("请发送同意或拒绝")
                        ]))

            try:
                if await asyncio.wait_for(self.inc.wait(waiter), timeout=300):
                    if self.bot_invited_join.groupId not in ACTIVE_GROUP:
                        BotGroup(self.bot_invited_join.groupId, active=1)
                        ACTIVE_GROUP.update({self.bot_invited_join.groupId: '*'})
                    await self.bot_invited_join.accept()
                    await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
                        Plain("已同意申请并加入白名单")
                    ]))
                else:
                    await self.bot_invited_join.reject("主人拒绝加入该群")
                    await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([Plain("已拒绝申请")]))

            except asyncio.TimeoutError:
                await self.bot_invited_join.reject("由于主人长时间未审核，已自动拒绝")
                await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([Plain("申请超时已自动拒绝")]))


class BotJoinGroup(Event):
    """收到入群事件"""
    event_name = "BotJoinGroupEvent"

    async def process(self):
        config = Config()
        membernum = len(await self.app.getMemberList(self.bot_join_group.group))
        await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
            Plain("收到加入群聊事件"),
            Plain(f"\n群号：{self.bot_join_group.group.id}"),
            Plain(f"\n群名：{self.bot_join_group.group.name}"),
            Plain(f"\n群人数：{membernum}"),
        ]))
        print(ACTIVE_GROUP)
        if self.bot_join_group.group.id not in ACTIVE_GROUP:
            await safeSendGroupMessage(
                self.bot_join_group.group.id,
                MessageChain.create(
                    f"该群未在白名单中，正在退出，如有需要请联系{config.MASTER_QQ}申请白名单"
                )
            )
            await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create("该群未在白名单中，正在退出"))
            return await self.app.quitGroup(self.bot_join_group.group.id)

        await safeSendGroupMessage(
            self.bot_join_group.group.id,
            MessageChain.create(
                f"我是{config.MASTER_NAME}"
                f"的机器人{config.BOT_NAME}，"
                f"如果有需要可以联系主人QQ“{config.MASTER_QQ}”，"
                f"添加{config.BOT_NAME}好友后请私聊说明用途后即可拉进其他群，主人看到后会选择是否同意入群"
                f"\n{config.BOT_NAME}被群禁言后会自动退出该群。"
                "\n发送 <.help> 可以查看功能列表"
                "\n拥有管理员以上权限可以开关功能"
                f"\n注：@{config.BOT_NAME}可以触发聊天功能"
            )
        )


class BotLeaveKick(Event):
    """被踢出群"""
    event_name = "BotLeaveEventKick"

    async def process(self):
        try:
            with MysqlDao() as db:
                db.update('UPDATE `group` SET active=0 WHERE uid=%s', [self.bot_leave_kick.group.id])
            ACTIVE_GROUP.pop(self.bot_leave_kick.group.id)
        except Exception:
            pass

        for qq in ADMIN_USER:
            await self.app.sendFriendMessage(qq, MessageChain.create(
                "收到被踢出群聊事件"
                f"\r\n群号: {self.bot_leave_kick.group.id}"
                f"\r\n群名: {self.bot_leave_kick.group.name}"
                "\r\n已移出白名单"
            ))


class BotLeaveActive(Event):
    """主动退群"""
    event_name = "BotLeaveEventActive"

    async def process(self):
        try:
            with MysqlDao() as db:
                db.update('UPDATE `group` SET active=0 WHERE uid=%s', [self.bot_leave_active.group.id])
            ACTIVE_GROUP.pop(self.bot_leave_active.group.id)
        except Exception:
            pass

        for qq in ADMIN_USER:
            await self.app.sendFriendMessage(qq, MessageChain.create(
                "收到主动退出群聊事件"
                f"\r\n群号: {self.bot_leave_active.group.id}"
                f"\r\n群名: {self.bot_leave_active.group.name}"
                "\r\n已移出白名单"
            ))


class BotGroupPermissionChange(Event):
    """群内权限变动"""
    event_name = "BotGroupPermissionChangeEvent"

    async def process(self):
        for qq in ADMIN_USER:
            await self.app.sendFriendMessage(qq, MessageChain.create([
                Plain("收到权限变动事件"),
                Plain(f"\r\n群号: {self.bot_group_perm_change.group.id}"),
                Plain(f"\r\n群名: {self.bot_group_perm_change.group.name}"),
                Plain(f"\r\n权限变更为: {self.bot_group_perm_change.current}")
            ]))


class BotMute(Event):
    """被禁言"""
    event_name = "BotMuteEvent"

    async def process(self):
        try:
            with MysqlDao() as db:
                db.update('UPDATE `group` SET active=0 WHERE uid=%s', [self.bot_mute.group.id])
            ACTIVE_GROUP.pop(self.bot_mute.group.id)
        except Exception:
            pass
        for qq in ADMIN_USER:
            await self.app.sendFriendMessage(qq, MessageChain.create([
                Plain("收到禁言事件， 已退出该群，并移出白名单"),
                Plain(f"\r\n群号: {self.bot_mute.group.id}"),
                Plain(f"\r\n群名: {self.bot_mute.group.name}"),
                Plain(f"\r\n操作者: {self.bot_mute.operator.name} | {self.bot_mute.operator.id}")
            ]))
        await self.app.quitGroup(self.bot_mute.group)


class Nudge(Event):
    """被戳一戳"""
    event_name = "NudgeEvent"

    async def process(self):
        config = Config()
        if self.nudge.target == int(config.LOGIN_QQ):
            if self.nudge.context_type == "group":
                if member := await self.app.getMember(self.nudge.group_id, self.nudge.supplicant):
                    logger.info(f"机器人被群 <{member.group.name}> 中用户 <{member.name}> 戳了戳。")
                    if member.group.id in NUDGE_INFO.keys():
                        if member.id in NUDGE_INFO[member.group.id].keys():
                            period = NUDGE_INFO[member.group.id][member.id]["time"] + relativedelta(minutes=1)
                            if datetime.now() >= period:
                                NUDGE_INFO[member.group.id][member.id] = {"count": 0, "time": datetime.now()}
                            count = NUDGE_INFO[member.group.id][member.id]["count"] + 1
                            if count == 1:
                                try:
                                    await self.app.sendNudge(member)
                                except:
                                    pass
                                NUDGE_INFO[member.group.id][member.id] = {"count": count, "time": datetime.now()}
                            elif count == 2:
                                try:
                                    await self.app.sendNudge(member)
                                    await self.app.sendGroupMessage(
                                        member.group.id, MessageChain.create([
                                            Plain(text=f"不许戳了！")
                                        ])
                                    )
                                except:
                                    pass
                                NUDGE_INFO[member.group.id][member.id] = {"count": count, "time": datetime.now()}
                            elif count == 3:
                                try:
                                    await self.app.sendNudge(member)
                                    await self.app.sendGroupMessage(
                                        member.group.id, MessageChain.create([
                                            Plain(text=f"说了不许再戳了！")
                                        ])
                                    )
                                except:
                                    pass
                                NUDGE_INFO[member.group.id][member.id] = {"count": count, "time": datetime.now()}
                            elif count == 4:
                                try:
                                    await self.app.sendNudge(member)
                                except:
                                    pass
                                NUDGE_INFO[member.group.id][member.id] = {"count": count, "time": datetime.now()}
                            elif count == 5:
                                try:
                                    await self.app.sendNudge(member)
                                    await self.app.sendGroupMessage(
                                        member.group.id, MessageChain.create([
                                            Plain(text=f"呜呜呜你欺负我，不理你了！")
                                        ])
                                    )
                                except:
                                    pass
                                NUDGE_INFO[member.group.id][member.id] = {"count": count, "time": datetime.now()}
                            elif 6 <= count <= 9:
                                NUDGE_INFO[member.group.id][member.id] = {"count": count, "time": datetime.now()}
                            elif count == 10:
                                try:
                                    await self.app.sendNudge(member)
                                    await self.app.sendGroupMessage(
                                        member.group.id, MessageChain.create([
                                            Plain(text="你真的很有耐心欸。")
                                        ])
                                    )
                                except:
                                    pass
                        else:
                            NUDGE_INFO[member.group.id][member.id] = {"count": 1, "time": datetime.now()}
                            await self.app.sendNudge(member)
                    else:
                        NUDGE_INFO[member.group.id] = {member.id: {"count": 1, "time": datetime.now()}}
                        await self.app.sendNudge(member)
            else:
                if friend := await self.app.getFriend(self.nudge.supplicant):
                    logger.info(f"机器人被好友 <{friend.nickname}> 戳了戳。")
