import asyncio

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.settings import *
from app.entities.group import BotGroup
from app.entities.user import BotUser
from app.plugin.base import Plugin, InitDB
from app.util.control import Permission
from app.util.dao import MysqlDao
from app.util.decorator import permission_required
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.admin']
    brief_help = '\r\n[√]\t白名单: admin'
    full_help = \
        '.admin\t仅主人可用！\r\n' \
        '.admin au [qq]\t激活用户\r\n' \
        '.admin du [qq]\t禁用用户\r\n' \
        '.admin bu [qq]\t拉黑用户\r\n' \
        '.admin ag [qg]\t激活群组\r\n' \
        '.admin dg [qg]\t禁用群组'
    hidden = True

    @permission_required(level=Permission.MASTER)
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'au'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                BotUser(int(self.msg[1]), active=1)
                self.resp = MessageChain.create([Plain('激活成功！')])
                ACTIVE_USER.update({int(self.msg[1]): '*'})
                if int(self.msg[1]) in BANNED_USER:
                    BANNED_USER.remove(int(self.msg[1]))
            elif isstartswith(self.msg[0], 'du'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                BotUser(int(self.msg[1]), active=0).user_deactivate()
                self.resp = MessageChain.create([Plain('禁用成功！')])
                if int(self.msg[1]) in ACTIVE_USER:
                    ACTIVE_USER.pop(int(self.msg[1]))
                if int(self.msg[1]) in BANNED_USER:
                    BANNED_USER.remove(int(self.msg[1]))
            elif isstartswith(self.msg[0], 'bu'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                BotUser(int(self.msg[1]), active=-1).user_deactivate()
                self.resp = MessageChain.create([Plain('拉黑成功！')])
                BANNED_USER.append(int(self.msg[1]))
            elif isstartswith(self.msg[0], 'ag'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                BotGroup(int(self.msg[1]), active=1)
                self.resp = MessageChain.create([Plain('激活成功！')])
                ACTIVE_GROUP.update({int(self.msg[1]): '*'})
            elif isstartswith(self.msg[0], 'dg'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if int(self.msg[1]) not in ACTIVE_GROUP:
                    self.resp = MessageChain.create([Plain('未找到该群组！')])
                    return
                BotGroup(int(self.msg[1]), active=0).group_deactivate()
                self.resp = MessageChain.create([Plain('禁用成功！')])
                ACTIVE_GROUP.pop(int(self.msg[1]))
            elif isstartswith(self.msg[0], 'ul'):
                with MysqlDao() as db:
                    res = db.query("SELECT uid FROM user WHERE active=1")
                self.resp = MessageChain.create([Plain('\r\n'.join([f'{qq}' for qq in res]))])
            elif isstartswith(self.msg[0], 'bl'):
                with MysqlDao() as db:
                    res = db.query("SELECT uid FROM user WHERE active=-1")
                self.resp = MessageChain.create([Plain('\r\n'.join([f'{qq}' for qq in res]))])
            elif isstartswith(self.msg[0], 'gl'):
                with MysqlDao() as db:
                    res = db.query("SELECT uid FROM `group` WHERE active=1")
                self.resp = MessageChain.create([Plain('\r\n'.join([f'{group_id}' for group_id in res]))])
            else:
                self.args_error()
                return
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()


class DB(InitDB):

    async def process(self):
        with MysqlDao() as _db:
            _db.update(
                "create table if not exists user( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) null comment 'QQ', \
                    permission char not null comment '许可', \
                    active int not null comment '状态', \
                    admin int not null comment '管理', \
                    points int default 0 null comment '积分', \
                    signin_points int default 0 null comment '签到积分', \
                    english_answer int default 0 null comment '英语答题榜', \
                    last_login date comment '最后登陆', \
                    last_moving_bricks date null comment '最后搬砖时间', \
                    last_part_time_job date null comment '最后打工时间')"
            )
            _db.update(
                "create table if not exists `group`( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) null comment '群号', \
                    permission char not null comment '许可', \
                    active int not null comment '状态')"
            )
            _db.update(
                "create table if not exists kick( \
                    src char(12) null comment '来源QQ', \
                    dst char(12) null comment '目标QQ', \
                    time datetime null comment '被踢时间', \
                    point int null comment '消耗积分')"
            )
            _db.update(
                "create table if not exists steal( \
                    src char(12) null comment '来源QQ', \
                    dst char(12) null comment '目标QQ', \
                    time datetime null comment '被偷时间', \
                    point int null comment '偷取积分')"
            )


if __name__ == '__main__':
    a = Module(MessageChain.create([Plain(
        '.sys au 123'
    )]))
    asyncio.run(a.get_resp())
    print(a.resp)
