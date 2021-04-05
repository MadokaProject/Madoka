from app.util.dao import MysqlDao


class BotUser:
    def __init__(self, qq, active=0, admin=0):
        self.qq = qq
        self.active = active
        self.admin = admin
        self.user_register()

    def user_register(self):
        """添加用户"""
        with MysqlDao() as db:
            res = db.query(
                'SELECT * FROM friend_listener WHERE uid=%s',
                [self.qq]
            )
            if not res:
                res = db.update(
                    'INSERT INTO friend_listener (uid, permission, active, admin) VALUES (%s, %s, %s, %s)',
                    [self.qq, '*', self.active, self.admin]
                )
                if not res:
                    raise Exception()
