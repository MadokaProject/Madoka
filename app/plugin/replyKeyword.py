import asyncio

from graia.application import MessageChain
from graia.application.message.elements.internal import Plain

from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.decorator import permission_required
from app.util.tools import isstartswith


class Reply(Plugin):
    entry = ['.reply']
    brief_help = '\r\n▶自定义回复: reply'
    full_help = \
        '.reply add [keyword] [text]\t添加自定义回复\r\n' \
        '.reply modify [keyword] [text]\t修改自定义回复\r\n' \
        '.reply remove [keyword]\t删除自定义回复\r\n' \
        '.reply list\t列出自定义回复'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'add'):
                assert len(self.msg) == 3
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT * FROM group_reply WHERE uid=%s and keyword=%s',
                        [self.group.id, self.msg[1]]
                    )
                    if not res:
                        res = db.update(
                            'INSERT INTO group_reply(uid, keyword, text) VALUES (%s, %s, %s)',
                            [self.group.id, self.msg[1], self.msg[2]]
                        )
                        if res:
                            self.resp = MessageChain.create([
                                Plain('添加成功！')
                            ])
                    else:
                        self.resp = MessageChain.create([
                            Plain('添加失败！该关键词已存在')
                        ])
            elif isstartswith(self.msg[0], 'modify'):
                assert len(self.msg) == 3
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT * FROM group_reply WHERE uid=%s and keyword=%s',
                        [self.group.id, self.msg[1]]
                    )
                    if res:
                        res = db.update(
                            'UPDATE group_reply SET text=%s WHERE uid=%s and keyword=%s',
                            [self.msg[2], self.group.id, self.msg[1]]
                        )
                        if res:
                            self.resp = MessageChain.create([
                                Plain('修改成功！')
                            ])
                    else:
                        self.resp = MessageChain.create([
                            Plain('修改失败！该关键词不存在')
                        ])
            elif isstartswith(self.msg[0], 'remove'):
                assert len(self.msg) == 2
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT * FROM group_reply WHERE uid=%s and keyword=%s',
                        [self.group.id, self.msg[1]]
                    )
                    if res:
                        res = db.update(
                            'DELETE FROM group_reply WHERE uid=%s and keyword=%s',
                            [self.group.id, self.msg[1]]
                        )
                        if res:
                            self.resp = MessageChain.create([
                                Plain('删除成功！')
                            ])
                    else:
                        self.resp = MessageChain.create([
                            Plain('删除失败！该关键词不存在')
                        ])
            elif isstartswith(self.msg[0], 'list'):
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT keyword FROM group_reply WHERE uid=%s',
                        [self.group.id]
                    )
                    self.resp = MessageChain.create([
                        Plain('\n'.join(f'{key}' for key in res[0]) if res else '该群组暂未配置！')
                    ])
            else:
                self.args_error()
                return
        except PermissionError as e:
            print(e)
            self.exec_permission_error()
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            print(e)
            self.unkown_error()


if __name__ == '__main__':
    a = Reply(MessageChain.create([Plain(
        '.reply add 123456 测试'
    )]))
    asyncio.run(a.get_resp())
    print(a.resp)
