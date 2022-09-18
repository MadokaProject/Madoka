import random
from textwrap import fill
from typing import Union

from arclet.alconna import Alconna, Args, Arpamar, Option
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.model import Friend, Group, Member
from graia.scheduler import GraiaScheduler, timers
from loguru import logger
from prettytable import PrettyTable

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.entities.game import BotGame
from app.util.phrases import args_error, point_not_enough, unknown_error
from app.util.send_message import safeSendFriendMessage
from app.util.text2image import create_image
from app.util.tools import to_thread

from .database.database import Game as DBGame
from .sign_image_generator import get_sign_image

core: AppCore = AppCore()
config = core.get_config()
app: Ariadne = core.get_app()
sche: GraiaScheduler = core.get_scheduler()
manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry="gp",
    brief_help="经济系统",
    alc=Alconna(
        command="gp",
        options=[
            Option("signin", help_text="每日签到"),
            Option("get", help_text="获取今日签到图"),
            Option("tf", help_text="转账", args=Args["at", At]["money", int]),
            Option("rank", help_text="显示群内已注册成员资金排行榜"),
            Option("auto", args=Args["status", bool], help_text="每天消耗10%金币自动签到"),
        ],
        help_text="经济系统",
    ),
)
async def process(target: Union[Friend, Member], sender: Union[Friend, Group], command: Arpamar):
    options = command.options
    try:
        if not options:
            """查询资金"""
            user = BotGame(target.id)
            coin = await user.coins
            if isinstance(sender, Group):
                return MessageChain([At(target), Plain(f" 你的{config.COIN_NAME}为%d!" % int(coin))])
            else:
                return MessageChain([Plain(f" 你的{config.COIN_NAME}为%d!" % int(coin))])
        if options.get("signin"):
            """签到"""
            coin = random.randint(1, 101)
            qq = target.id
            if isinstance(target, Member):
                name = target.name
            else:
                name = target.nickname
            user = BotGame(qq, coin)
            if await user.is_signin:
                if isinstance(sender, Group):
                    return MessageChain([At(target), Plain(" 你今天已经签到过了！")])
                else:
                    return MessageChain([Plain(" 你今天已经签到过了！")])
            else:
                await user.sign_in()
                sign_image = await to_thread(
                    get_sign_image,
                    await user.uuid,
                    qq,
                    name,
                    coin,
                    await user.intimacy,
                    await user.intimacy_level,
                    await user.consecutive_days,
                    await user.total_days,
                )
            return MessageChain([Image(data_bytes=sign_image)])
        elif options.get("get"):
            """获取今日签到图"""
            qq = target.id
            if isinstance(target, Member):
                name = target.name
            else:
                name = target.nickname
            user = BotGame(qq)
            if not await user.is_signin:
                if isinstance(sender, Group):
                    return MessageChain([At(target), Plain(" 你今天还没有签到哦！")])
                else:
                    return MessageChain([Plain("你今天还没有签到哦！")])
            sign_image = await to_thread(
                get_sign_image,
                await user.uuid,
                qq,
                name,
                await user.today_coin,
                await user.intimacy,
                await user.intimacy_level,
                await user.consecutive_days,
                await user.total_days,
            )
            return MessageChain([Image(data_bytes=sign_image)])
        elif tf := options.get("tf"):
            tf_target = tf["at"].target
            coin = tf["money"]
            if coin <= 0:
                return args_error()
            user = BotGame(target.id)
            if await user.coins < coin:
                return point_not_enough()
            await user.update_coin(-coin)
            user = BotGame(tf_target, coin)
            await user.update_coin(coin)
            return MessageChain(
                [
                    At(target),
                    Plain(" 已转赠给"),
                    At(tf_target),
                    Plain(f" %d{config.COIN_NAME}！" % coin),
                ]
            )
        elif options.get("rank") and isinstance(sender, Group):
            group_user = {item.id: item.name for item in await app.get_member_list(sender)}
            resp = MessageChain([Plain(f"群内{config.COIN_NAME}排行:\n")])
            user = target.id
            index = 1
            msg = PrettyTable()
            msg.field_names = ["序号", "群昵称", f"{config.COIN_NAME}"]
            _user_rank = []
            for res in DBGame.select().order_by(DBGame.coins.desc()):
                if user == int(res.qid):
                    _user_rank = [
                        index,
                        fill(group_user[int(res.qid)], width=20),
                        res.coins,
                    ]
                if res.coins == 0 or int(res.qid) not in group_user.keys():
                    continue
                if index <= 30:
                    msg.add_row([index, fill(group_user[int(res.qid)], width=20), res.coins])
                if index > 30 and _user_rank:
                    msg.add_row(["====", "".join("=" for _ in range(40)), "====="])
                    msg.add_row(_user_rank)
                    break
                index += 1
            msg.align = "r"
            msg.align["群昵称"] = "l"
            resp.extend(MessageChain([Image(data_bytes=await create_image(msg.get_string()))]))
            return resp
        elif auto := options.get("auto"):
            status = 1 if auto["status"] else 0
            await BotGame(target.id).auto_signin(status)
            return MessageChain("开启成功，将于每日8点为您自动签到！" if status else "关闭成功！")
        else:
            return args_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()


@sche.schedule(timers.crontabify("0 7 * * * 0"))
async def auto_sing():
    logger.info("auto signin is running...")
    for res in DBGame.select().where(DBGame.auto_signin == 1):
        user = BotGame(res.qid, coin := random.randint(1, 101))
        if not await user.is_signin:
            consume = random.randint(0, int(coin * 0.3))
            if await user.reduce_coin(consume):
                await user.sign_in()
                logger.success(f"账号: {res.qid} 自动签到完成~")
                await safeSendFriendMessage(res.qid, MessageChain(f"今日份签到完成，消耗{consume}金币\n请发送.gp get查收"))
            else:
                await safeSendFriendMessage(res.qid, MessageChain("您的金币不足，无法完成自动签到"))


@sche.schedule(timers.crontabify("59 23 * * * 50"))
async def tasks():
    sign_info = await BotGame.count()
    total_rent = await BotGame.ladder_rent_collection(config)
    await app.send_friend_message(
        config.MASTER_QQ,
        MessageChain(
            [
                Plain(f"签到统计成功，昨日共有 {sign_info[0]} / {sign_info[1]} 人完成了签到，"),
                Plain(f"签到率为 {'{:.2%}'.format(sign_info[0] / sign_info[1])}\n"),
                Plain(f"今日收取了 {total_rent} {config.COIN_NAME}"),
            ]
        ),
    )
