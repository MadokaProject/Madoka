from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, At

from app.util.dao import MysqlDao


async def Reply(self):
    with MysqlDao() as db:
        res = db.query(
            'SELECT text FROM group_reply WHERE uid=%s and keyword=%s',
            [self.group.id, self.message.asDisplay()]
        )
        if res:
            resp = MessageChain.create([
                At(self.member.id), Plain(' ' + res[0][0])
            ])
            await self._do_send(resp)
