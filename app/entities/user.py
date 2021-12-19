from app.util.dao import MysqlDao


class BotUser:
    def __init__(self, qq, point: int = 0, active: int = 0, level: int = 1):
        self.qq = qq
        self.point = point
        self.active = active
        self.level = level
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
                        "INSERT INTO user (uid, points, active, level) VALUES (%s, %s, %s, %s)",
                        [self.qq, self.point, self.active, self.level]
                ):
                    raise Exception()
            elif self.active == 1:
                if not db.update("UPDATE user SET active=%s WHERE uid=%s", [self.active, self.qq]):
                    raise Exception()

    def user_deactivate(self) -> None:
        """取消激活"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM user WHERE uid=%s",
                [self.qq]
            )
            if res[0][0]:
                if not db.update("UPDATE user SET active=%s WHERE uid=%s", [self.active, self.qq]):
                    raise Exception()

    def get_level(self) -> int:
        """获取用户权限等级"""
        with MysqlDao() as db:
            res = db.query("SELECT level FROM user WHERE uid=%s", [self.qq])
            return int(res[0][0])

    def grant_level(self, new_level: int) -> None:
        """修改用户权限"""
        with MysqlDao() as db:
            db.update("UPDATE user SET level=%s WHERE uid=%s", [new_level, self.qq])

    def sign_in(self) -> None:
        """签到"""
        with MysqlDao() as db:
            res = db.update(
                "UPDATE user SET points=points+%s, signin_points=%s, last_login=CURDATE() WHERE uid=%s",
                [self.point, self.point, self.qq]
            )
            if not res:
                raise Exception()

    def update_point(self, point) -> None:
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

    def update_english_answer(self, num) -> None:
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

    def get_sign_in_status(self) -> bool:
        """查询签到状态"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM user WHERE uid=%s AND last_login=CURDATE()",
                [self.qq]
            )
            return res[0][0]

    def get_points(self) -> bool:
        """查询积分"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT points FROM user WHERE uid=%s",
                [self.qq]
            )
            return res[0][0]

    def kick(self, src, dst, point, num) -> bool:
        """踢
            :param src: 来源QQ
            :param dst: 目标QQ
            :param point: 掉落积分
            :param num: 每天最多次数
        """
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM kick WHERE src=%s AND dst=%s AND TO_DAYS(time)=TO_DAYS(now())",
                [src, dst]
            )
            if not res[0][0] < num:
                return False
            self.update_point(point)
            res = db.update(
                "INSERT INTO kick (src, dst, time, point) VALUES (%s, %s, NOW(), %s)",
                [src, dst, -point]
            )
            if not res:
                raise Exception()
        return True

    def steal(self, src, dst, point, num) -> bool:
        """偷对方积分
            :param src: 来源QQ
            :param dst: 目标QQ
            :param point: 偷取积分
            :param num: 每天最多次数
        """
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM steal WHERE src=%s AND dst=%s AND TO_DAYS(time)=TO_DAYS(now())",
                [src, dst]
            )
            if not res[0][0] < num:
                return False
            self.update_point(point)
            res = db.update(
                "INSERT INTO steal (src, dst, time, point) VALUES (%s, %s, NOW(), %s)",
                [src, dst, point]
            )
            if not res:
                raise Exception()
        return True

    def get_moving_bricks_status(self) -> bool:
        """查询搬砖状态"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM user WHERE uid=%s AND last_moving_bricks=CURDATE()",
                [self.qq]
            )
            return res[0][0]

    def moving_bricks(self) -> None:
        """搬砖"""
        with MysqlDao() as db:
            res = db.update(
                "UPDATE user SET points=points+%s, last_moving_bricks=CURDATE() WHERE uid=%s",
                [self.point, self.qq]
            )
            if not res:
                raise Exception()

    def get_work_status(self) -> bool:
        """查询打工状态"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM user WHERE uid=%s AND last_part_time_job=CURDATE()",
                [self.qq]
            )
            return res[0][0]

    def work(self) -> None:
        """打工"""
        with MysqlDao() as db:
            res = db.update(
                "UPDATE user SET points=points+%s, last_part_time_job=CURDATE() WHERE uid=%s",
                [self.point, self.qq]
            )
            if not res:
                raise Exception()
