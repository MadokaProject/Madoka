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
)
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl

from app.core.config import Config
from app.event import *
from app.util.tools import isstartswith


class EventController:
    """其他事件处理控制器"""

    def __init__(self, event_name, *args):
        self.event_name = event_name
        self.event = None
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
                self.event = arg
            elif isinstance(arg, NudgeEvent):
                self.event = arg
            elif isinstance(arg, BotInvitedJoinGroupRequestEvent):
                self.event = arg
            elif isinstance(arg, BotJoinGroupEvent):
                self.event = arg
            elif isinstance(arg, BotLeaveEventKick):
                self.event = arg
            elif isinstance(arg, BotLeaveEventActive):
                self.event = arg
            elif isinstance(arg, BotGroupPermissionChangeEvent):
                self.event = arg
            elif isinstance(arg, BotMuteEvent):
                self.event = arg
            elif isinstance(arg, MemberCardChangeEvent):
                self.event = arg
            elif isinstance(arg, MemberJoinEvent):
                self.event = arg
            elif isinstance(arg, MemberLeaveEventKick):
                self.event = arg
            elif isinstance(arg, MemberLeaveEventQuit):
                self.event = arg
            elif isinstance(arg, MemberHonorChangeEvent):
                self.event = arg

    async def process_event(self):
        config = Config()
        if config.ONLINE and config.DEBUG:
            return

        # 加载事件处理器
        for event in base.Event.__subclasses__():
            obj = event(self.app, self.inc, self.event)
            if isstartswith(self.event_name, obj.event_name):
                await obj.process()
