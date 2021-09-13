import asyncio

from graia.application import MessageChain
from graia.application.message.elements.internal import Plain

from app.core.settings import *
from app.entities.group import BotGroup
from app.entities.user import BotUser
from app.plugin.base import Plugin, initDB
from app.util.dao import MysqlDao
from app.util.decorator import permission_required
from app.util.tools import isstartswith


class Sys(Plugin):
    entry = ['.sys']
    brief_help = '\r\n▶系统: sys'
    full_help = \
        '.sys\t仅管理可用！\r\n' \
        '.sys au [qq]\t添加用户\r\n' \
        '.sys du [qq]\t移除用户\r\n' \
        '.sys ag [qg]\t添加群组\r\n' \
        '.sys dg [qg]\t移除群组'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'au'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                BotUser(int(self.msg[1]), active=1)
                self.resp = MessageChain.create([
                    Plain('添加成功！')
                ])
                ACTIVE_USER.update({
                    int(self.msg[1]): '*',
                })
            elif isstartswith(self.msg[0], 'du'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if int(self.msg[1]) not in ACTIVE_USER:
                    self.resp = MessageChain.create([Plain(
                        '未找到该用户！'
                    )])
                    return
                with MysqlDao() as db:
                    res = db.update('UPDATE user SET active=0 where uid=%s', [int(self.msg[1])])
                if res:
                    self.resp = MessageChain.create([
                        Plain('取消成功！')
                    ])
                    ACTIVE_USER.pop(int(self.msg[1]))
            elif isstartswith(self.msg[0], 'ag'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                BotGroup(int(self.msg[1]), active=1)
                self.resp = MessageChain.create([
                    Plain('添加成功！')
                ])
                ACTIVE_GROUP.update({
                    int(self.msg[1]): '*'
                })
            elif isstartswith(self.msg[0], 'dg'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if int(self.msg[1]) not in ACTIVE_GROUP:
                    self.resp = MessageChain.create([Plain(
                        '未找到该群组！'
                    )])
                    return
                with MysqlDao() as db:
                    res = db.update('UPDATE `group` SET active=0 WHERE uid=%s', [int(self.msg[1])])
                if res:
                    self.resp = MessageChain.create([
                        Plain('取消成功！')
                    ])
                    ACTIVE_GROUP.pop(int(self.msg[1]))
            elif isstartswith(self.msg[0], 'ul'):
                with MysqlDao() as db:
                    res = db.query(
                        "SELECT uid FROM user WHERE active=1"
                    )
                self.resp = MessageChain.create([Plain(
                    ''.join([f'{qq}\r\n' for (qq,) in res])
                )])
            elif isstartswith(self.msg[0], 'gl'):
                with MysqlDao() as db:
                    res = db.query(
                        "SELECT uid FROM `group` WHERE active=1"
                    )
                self.resp = MessageChain.create([Plain(
                    '\r\n'.join([f'{group_id}' for (group_id,) in res])
                )])
            else:
                self.args_error()
                return
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            print(e)
            self.unkown_error()


class DB(initDB):

    async def process(self):
        with MysqlDao() as _db:
            _db.update(
                "create table if not exists user( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) null comment 'QQ', \
                    active int not null comment '状态', \
                    admin int not null comment '管理', \
                    points int default 0 null comment '积分', \
                    english_answer int default 0 null comment '英语答题榜', \
                    last_login date comment '最后登陆')"
            )
            _db.update(
                "create table if not exists `group`( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) null comment '群号', \
                    permission char not null comment '许可', \
                    active int not null comment '状态')"
            )


if __name__ == '__main__':
    a = Sys(MessageChain.create([Plain(
        '.sys au 123'
    )]))
    asyncio.run(a.get_resp())
    print(a.resp)
