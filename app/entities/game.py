import math
import time
from datetime import date
from uuid import uuid4

from loguru import logger
from peewee import IntegrityError

from app.core.config import Config
from app.plugin.basic.__11_game.database.database import Game


class BotGame:
    def __init__(self, qq, coin: int = 0):
        self.qq = qq
        self.coin = coin
        self.user_register()

    def user_register(self) -> None:
        """注册用户"""
        if not Game.get_or_none(Game.qid == self.qq):
            while True:
                try:
                    Game.create(uuid=uuid4(), qid=self.qq)
                    break
                except IntegrityError:
                    logger.warning("UUID 重复，正在尝试重新注册")

    @property
    async def is_consecutive(self) -> bool:
        """是否连续签到"""
        if time.mktime(date.today().timetuple()) - await self.last_signin_time > 86400:
            return False
        return True

    @property
    async def uuid(self) -> str:
        """获取uuid"""
        return Game.get(Game.qid == self.qq).uuid

    @property
    async def last_signin_time(self) -> int:
        """获取上次签到时间"""
        res = Game.get(Game.qid == self.qq).last_signin_time
        return int(time.mktime(res.timetuple())) if res is not None else 0

    @property
    async def intimacy_level(self) -> int:
        """获取用户好感度等级"""
        return Game.get(Game.qid == self.qq).intimacy_level or 0

    @property
    async def intimacy(self) -> int:
        """获取用户好感度"""
        return Game.get(Game.qid == self.qq).intimacy or 0

    @property
    async def consecutive_days(self) -> int:
        """获取连续签到天数"""
        return Game.get(Game.qid == self.qq).consecutive_days or 0

    @property
    async def total_days(self) -> int:
        """获取总签到天数"""
        return Game.get(Game.qid == self.qq).total_days or 0

    @property
    async def today_coin(self) -> int:
        """获取当日签到金币"""
        return Game.get(Game.qid == self.qq).coin or 0

    async def upgrade_intimacy_level(self) -> None:
        """修改用户好感度等级"""
        Game.update(intimacy_level=await self.intimacy_level + 1).where(Game.qid == self.qq).execute()

    async def grant_intimacy(self, intimacy: int) -> None:
        """修改用户好感度

        :param intimacy: 好感度变动值
        """
        now_level = await self.intimacy_level
        intimacy = await self.intimacy + intimacy
        intimacy_by_level = self.get_intimacy_by_level(now_level)
        difference = intimacy - intimacy_by_level
        if difference >= 0:
            intimacy = difference
            await self.upgrade_intimacy_level()
        Game.update(intimacy=intimacy).where(Game.qid == self.qq).execute()

    async def grant_consecutive_days(self, num: int) -> None:
        """修改用户连续签到天数

        :param num: 连续签到天数变动值
        """
        Game.update(consecutive_days=num).where(Game.qid == self.qq).execute()

    async def sign_in(self) -> None:
        """签到"""
        if await self.is_consecutive:  # 判断是否连续签到
            consecutive_days = await self.consecutive_days + 1
        else:
            consecutive_days = 1
        await self.grant_consecutive_days(consecutive_days)  # 修改连续签到天数
        consecutive_days = min(consecutive_days, 7)
        await self.grant_intimacy(self.get_intimacy_by_consecutive_days(consecutive_days))  # 好感度调整

        Game.update(
            coin=self.coin,
            coins=await self.coins + self.coin,
            last_signin_time=date.today(),
            total_days=await self.total_days + 1,
        ).where(Game.qid == self.qq).execute()

    @property
    async def coins(self) -> int:
        """查询金币"""
        return Game.get(Game.qid == self.qq).coins or 0

    async def update_coin(self, coin: int) -> None:
        """修改金币

        :param coin: 金币变动值
        """
        Game.update(coins=Game.get(Game.qid == self.qq).coins + coin).where(Game.qid == self.qq).execute()

    @property
    async def is_signin(self) -> bool:
        """查询是否签到"""
        return Game.select().where(Game.qid == self.qq, Game.last_signin_time == date.today()).exists()

    async def reduce_coin(self, coin: int) -> bool:
        """消耗金币

        :param coin: 消耗的金币数量
        """
        if await self.coins < coin:
            return False
        await self.update_coin(-coin)
        return True

    async def update_english_answer(self, num: int) -> None:
        """修改英语答题榜

        :param num: 答题变动值
        """
        Game.update(english_answer=Game.get(Game.qid == self.qq).english_answer + num).where(
            Game.qid == self.qq
        ).execute()

    async def auto_signin(self, status: int) -> None:
        """自动签到开关

        :param status: 开关状态
        """
        Game.update(auto_signin=status).where(Game.qid == self.qq).execute()

    @classmethod
    async def count(cls) -> tuple:
        """获取当日签到人数

        :return: (当日签到人数, 总人数)
        """
        return (
            Game.select().where(Game.last_signin_time == date.today()).count(),
            Game.select().count(),
        )

    @classmethod
    async def ladder_rent_collection(cls, config: Config) -> int:
        """收租

        :param config: Config 类
        :return: 总租金
        """
        total_rent = 0
        for user in Game.select().where(Game.coins >= 1000).order_by(Game.coins.desc()):
            ladder_rent = int((1 - (math.floor(user.coins / 1000) / 100)) * user.coins)
            Game.update(coins=ladder_rent).where(Game.qid == user.qid).execute()
            total_rent += user.coins - ladder_rent
            logger.info(f"{user.qid} 被收取 {user.coins - ladder_rent} {config.COIN_NAME}")
        return total_rent

    @classmethod
    def get_intimacy_by_level(cls, level: int) -> int:
        """根据等级给出所需的好感度

        :param level: 等级
        """
        if level == 0:
            return 0
        elif level == 1:
            return 10000
        return 10000 * level - (level - 1) * 1500 + 5000

    @classmethod
    def get_intimacy_by_consecutive_days(cls, consecutive_days: int) -> int:
        """根据连续签到天数给出增加的好感度

        :param consecutive_days: 连续签到天数
        """
        if consecutive_days < 1:
            return 0
        if consecutive_days == 1:
            return 300
        return 350 * consecutive_days - 50 * (consecutive_days - 1)
