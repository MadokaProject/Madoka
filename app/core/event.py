from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import (
    NewFriendRequestEvent,
    NudgeEvent,
    BotInvitedJoinGroupRequestEvent,
    BotJoinGroupEvent,
    BotLeaveEventKick,
    BotLeaveEventActive,
    BotGroupPermissionChangeEvent,
    BotMuteEvent,
    MemberCardChangeEvent,
    MemberJoinEvent,
    MemberLeaveEventKick,
    MemberLeaveEventQuit,
    MemberHonorChangeEvent,
    GroupRecallEvent
)
from loguru import logger

from app.core.app import AppCore
from app.event.event import EventController

core: AppCore = AppCore.get_core_instance()
bcc = core.get_bcc()
inc = core.get_inc()


@bcc.receiver("NewFriendRequestEvent")
async def new_friend_request_listener(app: Ariadne, event: NewFriendRequestEvent):
    event = EventController("NewFriendRequestEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("NudgeEvent")
async def nudge_listener(app: Ariadne, event: NudgeEvent):
    event = EventController("NudgeEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("BotInvitedJoinGroupRequestEvent")
async def bot_invited_join_group_request_listener(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    event = EventController("BotInvitedJoinGroupRequestEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("BotJoinGroupEvent")
async def bot_join_group_listener(app: Ariadne, event: BotJoinGroupEvent):
    event = EventController("BotJoinGroupEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("BotLeaveEventKick")
async def bot_leave_kick_listener(app: Ariadne, event: BotLeaveEventKick):
    event = EventController("BotLeaveEventKick", app, inc, event)
    await event.process_event()


@bcc.receiver("BotLeaveEventActive")
async def bot_leave_active_listener(app: Ariadne, event: BotLeaveEventActive):
    event = EventController("BotLeaveEventActive", app, inc, event)
    await event.process_event()


@bcc.receiver("BotGroupPermissionChangeEvent")
async def bot_group_permission_change_listener(app: Ariadne, event: BotGroupPermissionChangeEvent):
    event = EventController("BotGroupPermissionChangeEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("BotMuteEvent")
async def bot_mute_listener(app: Ariadne, event: BotMuteEvent):
    event = EventController("BotMuteEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberCardChangeEvent")
async def member_card_change_listener(app: Ariadne, event: MemberCardChangeEvent):
    event = EventController("MemberCardChangeEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberJoinEvent")
async def member_join_listener(app: Ariadne, event: MemberJoinEvent):
    event = EventController("MemberJoinEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberLeaveEventKick")
async def member_leave_kick_listener(app: Ariadne, event: MemberLeaveEventKick):
    event = EventController("MemberLeaveEventKick", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberLeaveEventQuit")
async def member_leave_quit_listener(app: Ariadne, event: MemberLeaveEventQuit):
    event = EventController("MemberLeaveEventQuit", app, inc, event)
    await event.process_event()


@bcc.receiver("MemberHonorChangeEvent")
async def member_honor_change_listener(app: Ariadne, event: MemberHonorChangeEvent):
    event = EventController("MemberHonorChangeEvent", app, inc, event)
    await event.process_event()


@bcc.receiver("GroupRecallEvent")
async def group_recall_listener(app: Ariadne, event: GroupRecallEvent):
    event = EventController("GroupRecallEvent", app, inc, event)
    await event.process_event()


logger.success("事件监听器启动成功")
