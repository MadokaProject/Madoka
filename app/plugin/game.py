import random

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, At
from loguru import logger
from prettytable import PrettyTable

from app.core.config import Config
from app.entities.user import BotUser
from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.control import Permission
from app.util.text2image import create_image
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.gp', '.货币']
    brief_help = '\r\n[√]\t货币：gp'
    full_help = \
        '.货币/.gp\t可以查询当前货币总量。\r\n' \
        '.货币/.gp 签到/signin [幸运儿/lucky | 倒霉蛋/unlucky]\t每天可以签到随机获取货币\r\n' \
        '.货币/.gp 转给/tf @user num\t转给XX num货币\r\n' \
        '.货币/.gp 充值/pay @user num\t充值XX num货币\r\n' \
        '.货币/.gp 排行/rank\t显示群内已注册成员货币排行榜'

    async def process(self):
        try:
            config = Config()
            if not self.msg:
                """查询货币"""
                user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id)
                point = await user.get_points()
                if hasattr(self, 'group'):
                    self.resp = MessageChain.create([
                        At(self.member.id),
                        Plain(f' 你的{config.COIN_NAME}为%d!' % int(point))
                    ])
                else:
                    self.resp = MessageChain.create([
                        Plain(f' 你的{config.COIN_NAME}为%d!' % int(point))
                    ])
                return
            if isstartswith(self.msg[0], ['签到', 'signin']):
                """签到"""
                if len(self.msg) > 1 and self.msg[1] in ['幸运儿', 'lucky', '倒霉蛋', 'unlucky']:
                    with MysqlDao() as db:
                        res = db.query(
                            'SELECT uid, signin_points FROM user WHERE last_login=CURDATE() and signin_points>70 '
                            'ORDER BY signin_points DESC ' if self.msg[1] in ['幸运儿', 'lucky'] else
                            'SELECT uid, signin_points FROM user WHERE last_login=CURDATE() and signin_points<30 '
                            'ORDER BY signin_points '
                        )
                        if not res:
                            self.resp = MessageChain.create([Plain('今日还未诞生 [幸运儿 | 倒霉蛋]')])
                            return
                        members = await self.app.getMemberList(self.group.id)
                        group_user = {item.id: item.name for item in members}
                        self.resp = MessageChain.create(
                            [Plain('群内今日签到幸运儿：\r\n' if self.msg[1] in ['幸运儿', 'lucky'] else '群内今日签到倒霉蛋：\r\n')])
                        index = 1
                        msg = PrettyTable()
                        msg.field_names = ['序号', '群昵称', f'签到{config.COIN_NAME}']
                        for qid, signin_points in res[:10]:
                            if int(qid) not in group_user.keys() or signin_points == 0:
                                continue
                            msg.add_row([index, group_user[int(qid)], signin_points])
                            index += 1
                        msg.align = 'r'
                        msg.align['群昵称'] = 'l'
                        self.resp.extend(MessageChain.create([
                            Image(data_bytes=(await create_image(msg.get_string())).getvalue())
                        ]))
                    return
                point = random.randint(1, 101)
                user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id, point)
                if await user.get_sign_in_status():
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
                    await user.sign_in()
                    if hasattr(self, 'group'):
                        self.resp = MessageChain.create([
                            At(self.member.id),
                            Plain(f' 签到成功，%s获得%d{config.COIN_NAME}' % (
                                '运气爆棚！' if point >= 90 else '', point
                            )),
                        ])
                    else:
                        self.resp = MessageChain.create([
                            Plain(f' 签到成功，%s获得%d{config.COIN_NAME}' % (
                                '运气爆棚！' if point >= 90 else '', point
                            )),
                        ])
            elif isstartswith(self.msg[0], ['转给', '转账', 'tf']):
                """转账"""
                assert len(self.msg) == 3 and self.message.has(At)
                target = self.message.getFirst(At).target
                point = int(self.msg[2])
                print(point)
                if point <= 0:
                    self.args_error()
                    return
                user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id)
                if int(await user.get_points()) < point:
                    self.point_not_enough()
                    return
                await user.update_point(-point)
                user = BotUser(target, point)
                await user.update_point(point)
                self.resp = MessageChain.create([
                    At(self.member.id),
                    Plain(' 已转赠给'),
                    At(target),
                    Plain(f' %d{config.COIN_NAME}！' % point)
                ])
            elif isstartswith(self.msg[0], ['排行', 'rank']):
                with MysqlDao() as db:
                    res = db.query(
                        "SELECT uid, points FROM user ORDER BY points DESC"
                    )
                    members = await self.app.getMemberList(self.group.id)
                    group_user = {item.id: item.name for item in members}
                    self.resp = MessageChain.create([Plain(f'群内{config.COIN_NAME}排行：\r\n')])
                    index = 1
                    msg = PrettyTable()
                    msg.field_names = ['序号', '群昵称', f'{config.COIN_NAME}']
                    for qid, point in res:
                        if point == 0 or int(qid) not in group_user.keys():
                            continue
                        msg.add_row([index, group_user[int(qid)], point])
                        index += 1
                    msg.align = 'r'
                    msg.align['群昵称'] = 'l'
                    self.resp.extend(MessageChain.create([
                        Image(data_bytes=(await create_image(msg.get_string())).getvalue())
                    ]))
            elif isstartswith(self.msg[0], ['充值', 'pay']):
                assert len(self.msg) == 3 and self.message.has(At)
                target = self.message.getFirst(At).target
                point = int(self.msg[2])
                if point <= 0:
                    self.args_error()
                    return
                if Permission.require(self.member, Permission.MASTER):
                    await BotUser(target).update_point(point)
                    self.resp = MessageChain.create([
                        At(self.member.id),
                        Plain(' 已充值给'),
                        At(target),
                        Plain(f' %d{config.COIN_NAME}！' % point)
                    ])
            else:
                self.args_error()
        except AssertionError:
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
