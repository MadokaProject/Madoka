from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.plugin.base import Plugin, initDB
from app.util.dao import MysqlDao
from app.util.decorator import permission_required
from app.util.tools import isstartswith


class GroupJoin(Plugin):
    entry = ['.join']
    brief_help = '\r\n[√]\t入群欢迎: join'
    full_help = \
        '.join\t仅管理可用\r\n' \
        '.join set [群号] [文本]\t设置入群欢迎消息\r\n' \
        '.join view [群号]\t查看入群欢迎消息\r\n' \
        '.join enable [群号]\t开启入群欢迎\r\n' \
        '.join disable [群号]\t关闭入群欢迎\r\n' \
        '.join drop [群号]\t删除入群欢迎\r\n' \
        '.join list\t查看已配置入群欢迎的群组'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'set'):
                assert len(self.msg) >= 3 and self.msg[1].isdigit()
                with MysqlDao() as db:
                    res = db.update(
                        'INSERT INTO group_join(uid, text, active) VALUES (%s, %s, %s)',
                        [self.group.id if self.msg[1] == '1' else self.msg[1],
                         '\n'.join([f'{value}' for value in self.msg[2:]]), 1]
                    )
                    self.resp = MessageChain.create([
                        Plain("设置成功！" if res else "设置失败！")
                    ])
            elif isstartswith(self.msg[0], 'view'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT text, active FROM group_join WHERE uid=%s',
                        [self.group.id if self.msg[1] == '1' else self.msg[1]]
                    )
                    self.resp = MessageChain.create([Plain(
                        ''.join([f'欢迎消息：{text}\n开启状态：{active}' for (text, active) in res]) if res else "该群组未配置欢迎消息！"
                    )])
            elif isstartswith(self.msg[0], 'enable'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                with MysqlDao() as db:
                    res = db.update(
                        'UPDATE group_join SET active=%s WHERE uid=%s',
                        [1, self.group.id if self.msg[1] == '1' else self.msg[1]]
                    )
                    self.resp = MessageChain.create([
                        Plain("开启成功！" if res else "开启失败，未找到该群组！")
                    ])
            elif isstartswith(self.msg[0], 'disable'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                with MysqlDao() as db:
                    res = db.update(
                        'UPDATE group_join SET active=%s WHERE uid=%s',
                        [0, self.group.id if self.msg[1] == '1' else self.msg[1]]
                    )
                    self.resp = MessageChain.create([
                        Plain("关闭成功！" if res else "关闭失败，未找到该群组！")
                    ])
            elif isstartswith(self.msg[0], 'drop'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                with MysqlDao() as db:
                    res = db.update(
                        'DELETE FROM group_join WHERE uid=%s',
                        [self.group.id if self.msg[1] == '1' else self.msg[1]]
                    )
                    self.resp = MessageChain.create([
                        Plain("删除成功！" if res else "删除失败，未找到该群组！")
                    ])
            elif isstartswith(self.msg[0], 'list'):
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT uid, active FROM group_join'
                    )
                    self.resp = MessageChain.create([Plain(
                        '\n'.join([f'群组：{uid}\t开启状态：{active}' for (uid, active) in res]) if res else "没有已配置入群欢迎的群组！"
                    )])
            else:
                self.args_error()
                return
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()


class DB(initDB):

    async def process(self):
        with MysqlDao() as _db:
            _db.update(
                "create table if not exists group_join( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) not null comment '群号', \
                    text varchar(200) not null comment '欢迎消息', \
                    active int not null comment '开关')"
            )
