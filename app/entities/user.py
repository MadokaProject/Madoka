from app.util.dao import MysqlDao


class BotUser:
    def __init__(self, qq, point=0, active=0, admin=0):
        self.qq = qq
        self.point = point
        self.active = active
        self.admin = admin
        self.user_register()

    def user_register(self):
        """注册用户"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM user WHERE uid=%s",
                [self.qq]
            )
            if not res[0][0]:
                res = db.update(
                    "INSERT INTO user (uid, points, active, admin) VALUES (%s, %s, %s, %s)",
                    [self.qq, self.point, self.active, self.admin]
                )
                if not res:
                    raise Exception()

    def sign_in(self):
        """签到"""
        with MysqlDao() as db:
            res = db.update(
                "UPDATE user SET points=points+%s, signin_points=%s, last_login=CURDATE() WHERE uid=%s",
                [self.point, self.point, self.qq]
            )
            if not res:
                raise Exception()

    def update_point(self, point):
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

    def update_english_answer(self, num):
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
