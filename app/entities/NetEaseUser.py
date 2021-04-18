from app.util.dao import MysqlDao


class NetEaseUser:
    def __init__(self, qq, phone, pwd):
        self.qq = qq
        self.phone = phone
        self.pwd = pwd
        self.user_register()

    def user_register(self):
        """添加用户"""
        with MysqlDao() as db:
            res = db.query(
                'SELECT * FROM netease WHERE phone=%s',
                [self.phone]
            )
            if not res:
                res = db.update(
                    'INSERT INTO netease (qid, phone, pwd) VALUES (%s, %s, %s)',
                    [self.qq, self.phone, self.pwd]
                )
                if not res:
                    raise Exception()
