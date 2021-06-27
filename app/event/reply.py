import re

from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, Image, At

from app.util.dao import MysqlDao

regex = re.compile(
    r'^(?:http)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


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


async def Repeat(self):
    with MysqlDao() as db:
        res = db.query(
            'SELECT content FROM msg WHERE uid=%s ORDER BY id desc limit 2',
            [self.group.id]
        )
        if res and res[0] == res[1] == self.message.asDisplay():
            if '请使用最新版手机QQ体验新功能' in res[0][0]:
                return
            resp = MessageChain.create([
                Image.fromNetworkAddress(res[0][0]) if re.match(regex, res[0][0]) else Plain(res[0][0])
            ])
            await self._do_send(resp)


if __name__ == '__main__':
    if re.match(regex,
                "http://gchat.qpic.cn/gchatpic_new/2627257869/1079235756-2438246460-DC608F995E41008C76A3BDDC744754F2/0?term=2"):
        print('True')
    else:
        print('False')
