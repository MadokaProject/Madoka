from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import (
    NewFriendRequestEvent,
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
)
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl


class Event:
    """事件处理继承此父类，并重写下面一个参数

    event_name: 事件名, 需与 EventController 事件名对应
    """
    event_name = '事件名'

    def __init__(self, *args):
        for arg in args:
            if isinstance(arg, Group):
                self.group = arg
            elif isinstance(arg, Member):
                self.member = arg
            elif isinstance(arg, Ariadne):
                self.app = arg
            elif isinstance(arg, InterruptControl):
                self.inc = arg
            elif isinstance(arg, NewFriendRequestEvent):
                self.new_friend = arg
            elif isinstance(arg, BotInvitedJoinGroupRequestEvent):
                self.bot_invited_join = arg
            elif isinstance(arg, BotJoinGroupEvent):
                self.bot_join_group = arg
            elif isinstance(arg, BotLeaveEventKick):
                self.bot_leave_kick = arg
            elif isinstance(arg, BotLeaveEventActive):
                self.bot_leave_active = arg
            elif isinstance(arg, BotGroupPermissionChangeEvent):
                self.bot_group_perm_change = arg
            elif isinstance(arg, BotMuteEvent):
                self.bot_mute = arg
            # elif isinstance(arg, NudgeEvent):
            #     self.event = arg
            elif isinstance(arg, MemberCardChangeEvent):
                self.member_card_change = arg
            elif isinstance(arg, MemberJoinEvent):
                self.member_join = arg
            elif isinstance(arg, MemberLeaveEventKick):
                self.member_leave_kick = arg
            elif isinstance(arg, MemberLeaveEventQuit):
                self.member_leave_quit = arg
            elif isinstance(arg, MemberHonorChangeEvent):
                self.member_honor_change = arg

    async def process(self):
        """子类必须重写此方法，此方法用于执行对应事件消息"""
        raise NotImplementedError
