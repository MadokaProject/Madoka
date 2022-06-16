import random

from arclet.alconna import Alconna, Option, Args, Arpamar
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, At
from graia.scheduler import GraiaScheduler, timers
from loguru import logger
from prettytable import PrettyTable

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.core.database import InitDB
from app.entities.game import BotGame
from app.entities.user import BotUser
from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.send_message import safeSendFriendMessage
from app.util.text2image import create_image
from app.util.tools import to_thread
from .game_res.sign_image_generator import get_sign_image

core: AppCore = AppCore.get_core_instance()
app: Ariadne = core.get_app()
sche: GraiaScheduler = core.get_scheduler()
manager: CommandDelegateManager = CommandDelegateManager.get_instance()
database: InitDB = InitDB.get_instance()


@manager.register(
    entry='gp',
    brief_help='经济系统',
    alc=Alconna(
        headers=manager.headers,
        command='gp',
        options=[
            Option('signin', help_text='每日签到'),
            Option('get', help_text='获取今日签到图'),
            Option('tf', help_text='转账', args=Args['at': At, 'money': int]),
            Option('迁移', help_text='迁移旧版金币'),
            Option('rank', help_text='显示群内已注册成员资金排行榜'),
            Option('auto', args=Args['status': bool], help_text='每天消耗10%金币自动签到')
        ],
        help_text='经济系统'
    )
)
async def process(self: Plugin, command: Arpamar, _: Alconna):
    options = command.options
    try:
        config = Config.get_instance()
        if not options:
            """查询资金"""
            user = BotGame((getattr(self, 'friend', None) or getattr(self, 'member', None)).id)
            coin = await user.get_coins()
            if hasattr(self, 'group'):
                return MessageChain.create([At(self.member.id), Plain(f' 你的{config.COIN_NAME}为%d!' % int(coin))])
            else:
                return MessageChain.create([Plain(f' 你的{config.COIN_NAME}为%d!' % int(coin))])
        if options.get('signin'):
            """签到"""
            coin = random.randint(1, 101)
            if hasattr(self, 'group'):
                qq = self.member.id
                name = self.member.name
            else:
                qq = self.friend.id
                name = self.friend.nickname
            user = BotGame(qq, coin)
            if await user.get_sign_in_status():
                if hasattr(self, 'group'):
                    return MessageChain.create([At(self.member.id), Plain(' 你今天已经签到过了！')])
                else:
                    return MessageChain.create([Plain(' 你今天已经签到过了！')])
            else:
                await user.sign_in()
                sign_image = await to_thread(
                    get_sign_image,
                    await user.get_uuid(),
                    qq,
                    name,
                    coin,
                    await user.get_intimacy(),
                    await user.get_intimacy_level(),
                    await user.get_consecutive_days(),
                    await user.get_total_days()
                )
            return MessageChain.create([Image(data_bytes=sign_image)])
        elif options.get('get'):
            """获取今日签到图"""
            if hasattr(self, 'group'):
                qq = self.member.id
                name = self.member.name
            else:
                qq = self.friend.id
                name = self.friend.nickname
            user = BotGame(qq)
            if not await user.get_sign_in_status():
                if hasattr(self, 'group'):
                    return MessageChain.create([At(self.member.id), Plain(' 你今天还没有签到哦！')])
                else:
                    return MessageChain.create([Plain('你今天还没有签到哦！')])
            sign_image = await to_thread(
                get_sign_image,
                await user.get_uuid(),
                qq,
                name,
                await user.get_today_coin(),
                await user.get_intimacy(),
                await user.get_intimacy_level(),
                await user.get_consecutive_days(),
                await user.get_total_days()
            )
            return MessageChain.create([Image(data_bytes=sign_image)])
        elif options.get('迁移'):
            old_user = BotUser((getattr(self, 'friend', None) or getattr(self, 'member', None)).id)
            new_user = BotGame((getattr(self, 'friend', None) or getattr(self, 'member', None)).id)
            coin = await old_user.get_points()
            if coin <= 0:
                return MessageChain.create([Plain('迁移失败，您的旧版账户中没有余额！')])
            await new_user.update_coin(coin)
            await old_user.update_point(-coin)
            return MessageChain.create([Plain(f'迁移成功！当前账户余额: {await new_user.get_coins()}')])
        elif tf := options.get('tf'):
            target = tf['at'].target
            coin = tf['money']
            if coin <= 0:
                return self.args_error()
            user = BotGame(self.member.id)
            if int(await user.get_coins()) < coin:
                return self.point_not_enough()
            await user.update_coin(-coin)
            user = BotGame(target, coin)
            await user.update_coin(coin)
            return MessageChain.create([
                At(self.member.id),
                Plain(' 已转赠给'),
                At(target),
                Plain(f' %d{config.COIN_NAME}！' % coin)
            ])
        elif options.get('rank'):
            with MysqlDao() as db:
                res = db.query(
                    "SELECT qid, coins FROM game ORDER BY coins DESC"
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
        elif auto := options.get('auto'):
            status = 1 if auto['status'] else 0
            await BotGame((getattr(self, 'friend', None) or getattr(self, 'member', None)).id).auto_signin(status)
            return MessageChain.create('开启成功，将于每日8点为您自动签到！' if status else '关闭成功！')
        else:
            return self.args_error()
    except Exception as e:
        logger.exception(e)
        return self.unkown_error()


@sche.schedule(timers.crontabify('0 8 * * * 0'))
async def auto_sing():
    logger.info('auto signin is running...')
    with MysqlDao() as db:
        res = db.query('SELECT qid FROM game WHERE auto_signin=1')
        for qq, in res:
            user = BotGame(qq, coin := random.randint(1, 101))
            if not await user.get_sign_in_status():
                consume = random.randint(0, int(coin * 0.1))
                if await user.reduce_coin(consume):
                    await user.sign_in()
                    logger.success(f'账号: {qq} 自动签到完成~')
                    await safeSendFriendMessage(qq, MessageChain.create(f'今日份签到完成，消耗{consume}金币\n请发送.gp get查收'))
                else:
                    await safeSendFriendMessage(qq, MessageChain.create("您的金币不足，无法完成自动签到"))


@database.init()
async def init_db():
    with MysqlDao() as db:
        db.update("""create table if not exists game (
                    uuid char(36) not null comment 'UUID',
                    qid char(12) not null comment 'QQ号',
                    consecutive_days int default 0 not null comment '连续签到天数',
                    total_days int default 0 not null comment '累计签到天数',
                    last_signin_time date comment '上次签到时间',
                    auto_signin int default 0 not null comment '自动签到',
                    coin int comment '今日获得货币',
                    coins int default 0 not null comment '货币',
                    intimacy int default 0 not null comment '好感度',
                    intimacy_level int default 0 not null comment '好感度等级',
                    english_answer int default 0 comment '英语答题榜',
                    primary key (uuid, qid)
            )""")
