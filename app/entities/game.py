import time
from datetime import date
from uuid import uuid4

from app.core.settings import IntimacyLevel, IntimacyGet
from app.util.dao import MysqlDao


class BotGame:
    def __init__(self, qq, coin: int = 0):
        self.qq = qq
        self.coin = coin
        self.user_register()

    def user_register(self) -> None:
        """注册用户"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM game WHERE qid=%s",
                [self.qq]
            )
            if not res[0][0]:
                while True:
                    if db.update(
                            "INSERT INTO game (uuid, qid) VALUES (%s, %s)",
                            [uuid4(), self.qq]
                    ):
                        break

    async def judge_consecutive_days(self) -> bool:
        """判断连续签到"""
        if time.mktime(date.today().timetuple()) - await self.get_last_signin_time() > 86400:
            return False
        return True

    async def get_uuid(self) -> str:
        with MysqlDao() as db:
            res = db.query("SELECT uuid FROM game WHERE qid=%s", [self.qq])
            return res[0][0]

    async def get_last_signin_time(self) -> int:
        """获取上次签到时间"""
        with MysqlDao() as db:
            res = db.query("SELECT last_signin_time FROM game WHERE qid=%s", [self.qq])
            if res[0][0] is None:
                return 0
            return int(time.mktime(res[0][0].timetuple()))

    async def get_intimacy_level(self) -> int:
        """获取用户好感度等级"""
        with MysqlDao() as db:
            res = db.query("SELECT intimacy_level FROM game WHERE qid=%s", [self.qq])
            if res[0][0] is None:
                return 0
            return res[0][0]

    async def get_intimacy(self) -> int:
        """获取用户好感度"""
        with MysqlDao() as db:
            res = db.query("SELECT intimacy FROM game WHERE qid=%s", [self.qq])
            if res[0][0] is None:
                return 0
            return res[0][0]

    async def get_consecutive_days(self) -> int:
        """获取连续签到天数"""
        with MysqlDao() as db:
            res = db.query("SELECT consecutive_days FROM game WHERE qid=%s", [self.qq])
            if res[0][0] is None:
                return 0
            return res[0][0]

    async def get_total_days(self) -> int:
        """获取总签到天数"""
        with MysqlDao() as db:
            res = db.query("SELECT total_days FROM game WHERE qid=%s", [self.qq])
            if res[0][0] is None:
                return 0
            return res[0][0]

    async def get_today_coin(self) -> int:
        """获取当日签到金币"""
        with MysqlDao() as db:
            res = db.query("SELECT coin FROM game WHERE qid=%s", [self.qq])
            if res[0][0] is None:
                return 0
            return res[0][0]

    async def upgrade_intimacy_level(self) -> None:
        """修改用户好感度等级"""
        with MysqlDao() as db:
            db.update("UPDATE game SET intimacy_level=intimacy_level+1 WHERE qid=%s", [self.qq])

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
        with MysqlDao() as db:
            db.update("UPDATE game SET intimacy=%s WHERE qid=%s", [intimacy, self.qq])

    async def grant_consecutive_days(self, num: int) -> None:
        """修改用户连续签到天数"""
        with MysqlDao() as db:
            db.update('UPDATE game SET consecutive_days=%s WHERE qid=%s', [num, self.qq])

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

        with MysqlDao() as db:
            res = db.update(
                "UPDATE game SET coin=%s, coins=coins+%s, last_signin_time=CURDATE(), total_days=total_days+1 "
                "WHERE qid=%s", [self.coin, self.coin, self.qq]
            )
            if not res:
                raise Exception()

    async def get_coins(self) -> int:
        """查询金币"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT coins FROM game WHERE qid=%s",
                [self.qq]
            )
            return res[0][0]

    async def update_coin(self, coin) -> None:
        """修改积分
        :param coin: str, 金币变动值
        """
        with MysqlDao() as db:
            res = db.update(
                "UPDATE game SET coins=coins+%s WHERE qid=%s",
                [coin, self.qq]
            )
            if not res:
                raise Exception()

    async def get_sign_in_status(self) -> bool:
        """查询签到状态"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM game WHERE qid=%s AND last_signin_time=CURDATE()",
                [self.qq]
            )
            return res[0][0]

    async def reduce_coin(self, coin: int) -> bool:
        if await self.get_coins() < coin:
            return False
        await self.update_coin(-coin)
        return True

    async def update_english_answer(self, num) -> None:
        """修改英语答题榜
        :param num: str, 答题变动值
        """
        with MysqlDao() as db:
            res = db.update(
                "UPDATE game SET english_answer=english_answer+%s WHERE qid=%s",
                [num, self.qq]
            )
            if not res:
                raise Exception()
