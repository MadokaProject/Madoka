import math
import time
from datetime import date
from uuid import uuid4
from peewee import IntegrityError
from loguru import logger

from app.core.config import Config
from app.core.settings import IntimacyLevel, IntimacyGet
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
                    pass

    async def judge_consecutive_days(self) -> bool:
        """判断连续签到"""
        if time.mktime(date.today().timetuple()) - await self.get_last_signin_time() > 86400:
            return False
        return True

    async def get_uuid(self) -> str:
        """获取uuid"""
        return Game.get(Game.qid == self.qq).uuid

    async def get_last_signin_time(self) -> int:
        """获取上次签到时间"""
        res = Game.get(Game.qid == self.qq).last_signin_time
        return int(time.mktime(res.timetuple())) if res is not None else 0

    async def get_intimacy_level(self) -> int:
        """获取用户好感度等级"""
        return Game.get(Game.qid == self.qq).intimacy_level or 0

    async def get_intimacy(self) -> int:
        """获取用户好感度"""
        return Game.get(Game.qid == self.qq).intimacy or 0

    async def get_consecutive_days(self) -> int:
        """获取连续签到天数"""
        return Game.get(Game.qid == self.qq).consecutive_days or 0

    async def get_total_days(self) -> int:
        """获取总签到天数"""
        return Game.get(Game.qid == self.qq).total_days or 0

    async def get_today_coin(self) -> int:
        """获取当日签到金币"""
        return Game.get(Game.qid == self.qq).coin or 0

    async def upgrade_intimacy_level(self) -> None:
        """修改用户好感度等级"""
        Game.update(
            intimacy_level=await self.get_intimacy_level() + 1
        ).where(Game.qid == self.qq).execute()

    async def grant_intimacy(self, intimacy: int) -> None:
        """修改用户好感度"""
        now_level = await self.get_intimacy_level()
        intimacy = await self.get_intimacy() + intimacy
        difference = intimacy - IntimacyLevel[now_level]
        if difference >= 0:  # 判断是否可以升级
            if now_level == 9:
                intimacy = IntimacyLevel[now_level]
            else:
                intimacy = difference
                await self.upgrade_intimacy_level()  # 进行升级
        Game.update(intimacy=intimacy).where(Game.qid == self.qq).execute()

    async def grant_consecutive_days(self, num: int) -> None:
        """修改用户连续签到天数"""
        Game.update(consecutive_days=num).where(Game.qid == self.qq).execute()

    async def sign_in(self) -> None:
        """签到"""
        if await self.judge_consecutive_days():  # 判断是否连续签到
            consecutive_days = await self.get_consecutive_days() + 1
        else:
            consecutive_days = 1
        await self.grant_consecutive_days(consecutive_days)  # 修改连续签到天数
        if consecutive_days >= 7:
            consecutive_days = 7
        await self.grant_intimacy(IntimacyGet[consecutive_days - 1])  # 好感度调整

        Game.update(
            coin=self.coin,
            coins=Game.get(Game.qid == self.qq).coins + self.coin,
            last_signin_time=date.today(),
            total_days=Game.get(Game.qid == self.qq).total_days + 1
        ).where(Game.qid == self.qq).execute()

    async def get_coins(self) -> int:
        """查询金币"""
        return Game.get(Game.qid == self.qq).coins

    async def update_coin(self, coin) -> None:
        """修改金币
        :param coin: str, 金币变动值
        """
        Game.update(coins=Game.get(Game.qid == self.qq).coins + coin).where(Game.qid == self.qq).execute()

    async def get_sign_in_status(self) -> bool:
        """查询签到状态"""
        return Game.select().where(Game.qid == self.qq, Game.last_signin_time == date.today()).exists()

    async def reduce_coin(self, coin: int) -> bool:
        """消耗金币"""
        if await self.get_coins() < coin:
            return False
        await self.update_coin(-coin)
        return True

    async def update_english_answer(self, num) -> None:
        """修改英语答题榜
        :param num: str, 答题变动值
        """
        Game.update(
            english_answer=Game.get(Game.qid == self.qq).english_answer + num
        ).where(Game.qid == self.qq).execute()

    async def auto_signin(self, status: int) -> None:
        """自动签到开关"""
        Game.update(auto_signin=status).where(Game.qid == self.qq).execute()

    @classmethod
    async def get_all_sign_num(cls) -> tuple:
        """获取当日签到人数"""
        return Game.select().where(Game.last_signin_time == date.today()).count(), Game.select().count()

    @classmethod
    async def ladder_rent_collection(cls, config: Config) -> int:
        """收租

        :return: 总租金
        """
        total_rent = 0
        for user in Game.select().where(Game.coins >= 1000).order_by(Game.coins.desc()):
            ladder_rent = int((1 - (math.floor(user.coins / 1000) / 100)) * user.coins)
            Game.update(coins=ladder_rent).where(Game.qid == user.qid).execute()
            total_rent += user.coins - ladder_rent
            logger.info(f"{user.qid} 被收取 {user.coins - ladder_rent} {config.COIN_NAME}")
        return total_rent
