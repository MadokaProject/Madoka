import random

from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, At

from app.entities.user import BotUser
from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.tools import isstartswith


class Game(Plugin):
    entry = ['.gp', '.积分']
    brief_help = '\r\n▶积分：gp'
    full_help = \
        '.积分/.gp\t可以查询当前积分总量。\r\n' \
        '.积分/.gp 签到/signin\t每天可以签到随机获取积分。\r\n' \
        '.积分/.gp 转给/tf@XX[num]\t转给XX num积分。\r\n' \
        '.积分/.gp 排行/rank\t显示群内已注册成员积分排行榜'

    async def process(self):
        if not self.msg:
            """查询积分"""
            try:
                user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id)
                point = user.get_points()
                if hasattr(self, 'group'):
                    self.resp = MessageChain.create([
                        At(self.member.id),
                        Plain(' 你的积分为%d!' % int(point))
                    ])
                else:
                    self.resp = MessageChain.create([
                        Plain(' 你的积分为%d!' % int(point))
                    ])
            except Exception as e:
                print(e)
                self.unkown_error()
            return
        if isstartswith(self.msg[0], ['签到', 'signin']):
            """签到"""
            try:
                point = random.randint(1, 101)
                user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id, point)
                if user.get_sign_in_status():
                    if hasattr(self, 'group'):
                        self.resp = MessageChain.create([
                            At(self.member.id),
                            Plain(' 你今天已经签到过了！'),
                        ])
                    else:
                        self.resp = MessageChain.create([
                            Plain(' 你今天已经签到过了！')
                        ])
                else:
                    user.sign_in()
                    if hasattr(self, 'group'):
                        self.resp = MessageChain.create([
                            At(self.member.id),
                            Plain(' 签到成功，%s获得%d积分' % (
                                '运气爆棚！' if point >= 90 else '', point
                            )),
                        ])
                    else:
                        self.resp = MessageChain.create([
                            Plain(' 签到成功，%s获得%d积分' % (
                                '运气爆棚！' if point >= 90 else '', point
                            )),
                        ])
            except Exception as e:
                print(e)
                self.unkown_error()
        elif isstartswith(self.msg[0], ['转给', '转账', 'tf']):
            """转账"""
            try:
                if len(self.msg) == 1:
                    self.args_error()
                    return
                point = int(self.msg[1])
                if point <= 0:
                    self.args_error()
                    return
                user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id)
                if int(user.get_points()) < point:
                    self.point_not_enough()
                    return
                target = self.message[At][0]
                if not target:
                    self.args_error()
                    return
                user.update_point(-point)
                user = BotUser(target.dict()['target'], point)
                user.update_point(point)
                self.resp = MessageChain.create([
                    At(self.member.id),
                    Plain(' 已转赠给'),
                    target,
                    Plain(' %d积分！' % point)
                ])
            except ValueError as e:
                print(e)
                self.arg_type_error()
            except Exception as e:
                print(e)
                self.unkown_error()
        elif isstartswith(self.msg[0], ['排行', 'rank']):
            try:
                with MysqlDao() as db:
                    res = db.query(
                        "SELECT uid, points FROM user ORDER BY points DESC"
                    )
                    members = await self.app.memberList(self.group.id)
                    group_user = {item.id: item.name for item in members}
                    self.resp = MessageChain.create([Plain('群内积分排行：\r\n')])
                    index = 1
                    for item in res:
                        if int(item[0]) in group_user.keys():
                            self.resp.plus(
                                MessageChain.create([Plain(
                                    '%d. ' % index + group_user[int(item[0])] + ': %d\r\n' % item[1]
                                )])
                            )
                            index += 1
            except Exception as e:
                print(e)
                self.unkown_error()
        else:
            self.args_error()
