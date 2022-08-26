from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.model import MemberPerm, Group

from app.core.settings import *
from app.plugin.basic.__01_sys.database.database import Msg as DBMsg
from app.trigger.trigger import Trigger
from app.util.control import Permission


class CSM(Trigger):
    """群管系统"""

    async def process(self):
        # 判断是否为黑名单用户
        if self.target.id in BANNED_USER:
            self.as_last = True
        if not isinstance(self.sender, Group) or Permission.manual(self.target, Permission.GROUP_ADMIN) or \
                self.sender.account_perm == MemberPerm.Member:
            return
        if str(self.sender.id) in CONFIG and 'status' in CONFIG[str(self.sender.id)] and \
                CONFIG[str(self.sender.id)]['status']:  # 默认关闭，需自行开启(.csm status)
            if await self.spam():  # 刷屏检测(优先)
                self.as_last = True

    # 刷屏检测
    async def spam(self):
        try:
            res = DBMsg.select().where(
                DBMsg.uid == self.sender.id,
                DBMsg.qid == self.target.id
            ).order_by(DBMsg.id.desc()).limit(3)  # 获取该群组某人的最后三条消息记录
            if res.count() > 2:
                time = (res[0].datetime - res[2].datetime).seconds
                flood = CONFIG[str(self.sender.id)].get('mute', {'time': 5, 'mute': 300, 'message': '请勿刷屏！'})
                duplicate = CONFIG[str(self.sender.id)].get(
                    'duplicate', {'time': 30, 'mute': 120, 'message': '请勿发送重复消息！'}
                )
                temp_content = MessageChain.from_persistent_string(res[0].content)
                if time < flood['time']:  # 刷屏禁言
                    await self.app.mute_member(self.sender, self.target, flood['mute'])
                    resp = MessageChain([
                        At(self.target.id), Plain(' ' + flood['message'])
                    ])
                    await self.do_send(resp)
                    return True
                elif all(MessageChain.from_persistent_string(i.content) == temp_content for i in res) \
                        and time < duplicate['time']:  # 发送重复消息禁言
                    await self.app.mute_member(self.sender, self.target, duplicate['mute'])
                    resp = MessageChain([
                        At(self.target), Plain(' ' + duplicate['message'])
                    ])
                    await self.do_send(resp)
                    return True
            over_length = CONFIG[str(self.sender.id)].get(
                'over-length', {'text': 500, 'mute': 120, 'message': '请勿发送超长消息'}
            )
            if len(self.message.display) > over_length['text']:
                await self.app.recall_message(self.source)
                await self.app.mute_member(self.sender, self.target, over_length['mute'])
                resp = MessageChain([
                    At(self.target.id), Plain(' ' + over_length['message'])
                ])
                await self.do_send(resp)
                return True
        except Exception as e:
            logger.exception(e)
