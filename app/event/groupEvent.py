from io import BytesIO

import httpx
from PIL import Image as IMG
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.model import MemberInfo

from app.core.config import Config
from app.core.settings import ADMIN_USER
from app.event.base import Event
from app.util.onlineConfig import get_config
from app.util.sendMessage import safeSendGroupMessage


class MemberCardChange(Event):
    """群名片被修改"""
    event_name = "MemberCardChangeEvent"

    async def process(self):
        config = Config()
        if self.member_card_change.member.id == int(config.LOGIN_QQ):
            if self.member_card_change.current != config.BOT_NAME:
                for qq in ADMIN_USER:
                    await self.app.sendFriendMessage(qq, MessageChain.create([
                        Plain(f"检测到 {config.BOT_NAME} 群名片变动"),
                        Plain(f"\n群号：{str(self.member_card_change.member.group.id)}"),
                        Plain(f"\n群名：{self.member_card_change.member.group.name}"),
                        Plain(f"\n被修改为：{self.member_card_change.current}"),
                        Plain(f"\n已为你修改回：{config.BOT_NAME}")
                    ]))
                await self.app.modifyMemberInfo(
                    group=self.member_card_change.member.group.id,
                    member=int(config.LOGIN_QQ),
                    info=MemberInfo(name=config.BOT_NAME),
                )
                await safeSendGroupMessage(
                    self.member_card_change.member.group.id, MessageChain.create([Plain("请不要修改我的群名片")])
                )
        else:
            await safeSendGroupMessage(self.member_card_change.member.group, MessageChain.create([
                At(self.member_card_change.member.id),
                Plain(f" 的群名片由 {self.member_card_change.origin} 被修改为 {self.member_card_change.current}")
            ]))


class MemberJoin(Event):
    """有人加入群聊"""
    event_name = "MemberJoinEvent"

    async def process(self):
        msg = [
            Image(url=f"http://q1.qlogo.cn/g?b=qq&nk={str(self.member_join.member.id)}&s=4"),
            Plain("\n欢迎 "),
            At(self.member_join.member.id),
            Plain(" 加入本群"),
        ]
        res = get_config('member_join', self.member_join.member.group.id)
        if res and res['active']:
            msg.append(Plain(f"\r\n{res['text']}") if res.__contains__('text') else None)
            await safeSendGroupMessage(self.member_join.member.group, MessageChain.create(msg))


class MemberLeaveKick(Event):
    """有人被踢出群聊"""
    event_name = "MemberLeaveEventKick"

    async def process(self):
        msg = [
            Image(data_bytes=await avater_blackandwhite(self.member_leave_kick.member.id)),
            Plain(f"\n{self.member_leave_kick.member.name} 被 "),
            At(self.member_leave_kick.operator.id),
            Plain(" 踢出本群"),
        ]
        await safeSendGroupMessage(self.member_leave_kick.member.group, MessageChain.create(msg))


class MemberLeaveQuit(Event):
    """有人退出群聊"""
    event_name = "MemberLeaveEventQuit"

    async def process(self):
        msg = [
            Image(data_bytes=await avater_blackandwhite(self.member_leave_quit.member.id)),
            Plain(f"\n{self.member_leave_quit.member.name} 退出本群"),
        ]
        await safeSendGroupMessage(self.member_leave_quit.member.group, MessageChain.create(msg))


class MemberHonorChange(Event):
    """有人群荣誉变动"""
    event_name = "MemberHonorChangeEvent"

    async def process(self):
        msg = [
            At(self.member_honor_change.member.id),
            Plain(
                f" {'获得了' if self.member_honor_change.action == 'achieve' else '失去了'} 群荣誉 {self.member_honor_change.honor}！"),
        ]
        await safeSendGroupMessage(self.member_honor_change.member.group, MessageChain.create(msg))


async def avater_blackandwhite(qq: int) -> bytes:
    """
    获取群成员头像黑白化
    """
    url = f"http://q1.qlogo.cn/g?b=qq&nk={str(qq)}&s=4"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    img = IMG.open(BytesIO(resp.content))
    img = img.convert("L")
    img.save(imgbio := BytesIO(), "JPEG")
    return imgbio.getvalue()
