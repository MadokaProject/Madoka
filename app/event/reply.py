from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, At

from app.util.dao import MysqlDao
from app.util.tools import message_source


async def ReplyS(self):
    async def Reply(self):  # 自定义消息回复
        if message_source(self):
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

    async def Repeat(self):  # +1 行为
        if message_source(self):
            with MysqlDao() as db:
                res = db.query(
                    'SELECT content FROM msg WHERE uid=%s ORDER BY id desc limit 3',
                    [self.group.id]
                )
                if res and res[0][0] == res[1][0] == res[2][0] and self.message.asDisplay():
                    if '请使用最新版手机QQ体验新功能' in res[0][0]:
                        return
                    resp = MessageChain.create([
                        Plain(res[0][0])
                    ])
                    await self._do_send(resp)

    await Reply(self)
    await Repeat(self)
