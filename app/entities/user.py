from app.util.dao import MysqlDao


class BotUser:
    def __init__(self, qq, point: int = 0, active: int = 0):
        self.qq = qq
        self.point = point
        self.active = active
        self.user_register()

    def user_register(self) -> None:
        """注册用户"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM user WHERE uid=%s",
                [self.qq]
            )
            if not res[0][0]:
                if not db.update(
                        "INSERT INTO user (uid, points, active) VALUES (%s, %s, %s)",
                        [self.qq, self.point, self.active]
                ):
                    raise Exception()
            elif self.active == 1:
                if not db.update("UPDATE user SET active=%s WHERE uid=%s", [self.active, self.qq]):
                    raise Exception()

    async def user_deactivate(self) -> None:
        """取消激活"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM user WHERE uid=%s",
                [self.qq]
            )
            if res[0][0]:
                if not db.update("UPDATE user SET active=%s WHERE uid=%s", [self.active, self.qq]):
                    raise Exception()

    async def get_level(self) -> int:
        """获取用户权限等级"""
        with MysqlDao() as db:
            res = db.query("SELECT level FROM user WHERE uid=%s", [self.qq])
            if res[0][0] is None:
                return -1
            return int(res[0][0])

    async def grant_level(self, new_level: int) -> None:
        """修改用户权限"""
        with MysqlDao() as db:
            db.update("UPDATE user SET level=%s WHERE uid=%s", [new_level, self.qq])

    async def sign_in(self) -> None:
        """签到"""
        with MysqlDao() as db:
            res = db.update(
                "UPDATE user SET points=points+%s, signin_points=%s, last_login=CURDATE() WHERE uid=%s",
                [self.point, self.point, self.qq]
            )
            if not res:
                raise Exception()

    async def update_point(self, point) -> None:
        """修改积分
        :param point: str, 积分变动值
        """
        with MysqlDao() as db:
            res = db.update(
                "UPDATE user SET points=points+%s WHERE uid=%s",
                [point, self.qq]
            )
            if not res:
                raise Exception()

    async def update_english_answer(self, num) -> None:
        """修改英语答题榜
        :param num: str, 答题变动值
        """
        with MysqlDao() as db:
            res = db.update(
                "UPDATE user SET english_answer=english_answer+%s WHERE uid=%s",
                [num, self.qq]
            )
            if not res:
                raise Exception()

    async def get_sign_in_status(self) -> bool:
        """查询签到状态"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM user WHERE uid=%s AND last_login=CURDATE()",
                [self.qq]
            )
            return res[0][0]

    async def get_points(self) -> bool:
        """查询积分"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT points FROM user WHERE uid=%s",
                [self.qq]
            )
            return res[0][0]

    async def reduce_gold(self, gold: int) -> bool:
        if await self.get_points() < gold:
            return False
        await self.update_point(-gold)
        return True
