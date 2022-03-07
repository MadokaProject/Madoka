import random

from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, At
from loguru import logger
from prettytable import PrettyTable

from app.core.command_manager import CommandManager
from app.core.config import Config
from app.entities.user import BotUser
from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.text2image import create_image


class Module(Plugin):
    entry = 'gp'
    brief_help = '经济系统'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('sign', help_text='每日签到', options=[
                Option('--lucky', alias='-l', help_text='查看今日幸运儿'),
                Option('--unlucky', alias='-ul', help_text='查看今日倒霉蛋')
            ]),
            Subcommand('tf', help_text='转账', args=Args['at': At, 'money': int]),
            Subcommand('rank', help_text='显示群内已注册成员资金排行榜')
        ],
        help_text='经济系统'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        other_args = command.other_args
        try:
            config = Config()
            if not subcommand:
                """查询资金"""
                user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id)
                point = await user.get_points()
                if hasattr(self, 'group'):
                    return MessageChain.create([At(self.member.id), Plain(f' 你的{config.COIN_NAME}为%d!' % int(point))])
                else:
                    return MessageChain.create([Plain(f' 你的{config.COIN_NAME}为%d!' % int(point))])
            if subcommand.__contains__('sign'):
                """签到"""
                if other_args.__contains__('lucky') or other_args.__contains__('unlucky'):
                    flag = other_args.__contains__('lucky')
                    with MysqlDao() as db:
                        res = db.query(
                            'SELECT uid, signin_points FROM user WHERE last_login=CURDATE() and signin_points>70 '
                            'ORDER BY signin_points DESC' if flag else
                            'SELECT uid, signin_points FROM user WHERE last_login=CURDATE() and signin_points<30 '
                            'ORDER BY signin_points'
                        )
                        if not res:
                            return MessageChain.create([Plain('今日还未诞生' + ('幸运儿' if flag else '倒霉蛋'))])
                        group_user = {item.id: item.name for item in await self.app.getMemberList(self.group.id)}
                        resp = MessageChain.create([Plain('群内今日签到幸运儿:\n' if flag else '群内今日签到倒霉蛋:\n')])
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
                        resp.extend(MessageChain.create([Image(data_bytes=await create_image(msg.get_string()))]))
                        return resp
                point = random.randint(1, 101)
                user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id, point)
                if await user.get_sign_in_status():
                    if hasattr(self, 'group'):
                        return MessageChain.create([At(self.member.id), Plain(' 你今天已经签到过了！')])
                    else:
                        return MessageChain.create([Plain(' 你今天已经签到过了！')])
                else:
                    await user.sign_in()
                    if hasattr(self, 'group'):
                        return MessageChain.create([
                            At(self.member.id),
                            Plain(f' 签到成功，%s获得%d{config.COIN_NAME}' % ('运气爆棚！' if point >= 90 else '', point)),
                        ])
                    else:
                        return MessageChain.create([
                            Plain(f' 签到成功，%s获得%d{config.COIN_NAME}' % ('运气爆棚！' if point >= 90 else '', point))
                        ])
            elif subcommand.__contains__('tf'):
                target = other_args['at'].target
                point = other_args['money']
                if point <= 0:
                    return self.args_error()
                user = BotUser(self.member.id)
                if int(await user.get_points()) < point:
                    return self.point_not_enough()
                await user.update_point(-point)
                user = BotUser(target, point)
                await user.update_point(point)
                return MessageChain.create([
                    At(self.member.id),
                    Plain(' 已转赠给'),
                    At(target),
                    Plain(f' %d{config.COIN_NAME}！' % point)
                ])
            elif subcommand.__contains__('rank'):
                with MysqlDao() as db:
                    res = db.query(
                        "SELECT uid, points FROM user ORDER BY points DESC"
                    )
                    group_user = {item.id: item.name for item in await self.app.getMemberList(self.group.id)}
                    resp = MessageChain.create([Plain(f'群内{config.COIN_NAME}排行:\n')])
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
                    resp.extend(MessageChain.create([
                        Image(data_bytes=await create_image(msg.get_string()))
                    ]))
                    return resp
            else:
                return self.args_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()
