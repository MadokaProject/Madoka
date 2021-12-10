from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At

from app.trigger.trigger import Trigger
from app.util.dao import MysqlDao


class Reply(Trigger):
    """自定义消息回复"""

    async def process(self):
        if not hasattr(self, 'group'):
            return
        if self.msg[0][0] in '.,;!?。，；！？/\\':  # 判断是否为指令
            return
        with MysqlDao() as db:
            res = db.query(
                'SELECT text FROM group_reply WHERE uid=%s and keyword=%s',
                [self.group.id, self.message.asDisplay()]
            )
            if res:
                resp = MessageChain.create([
                    At(self.member.id), Plain(' ' + res[0][0])
                ])
                await self.do_send(resp)
                self.as_last = True
