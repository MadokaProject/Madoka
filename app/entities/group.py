from app.util.dao import MysqlDao


class BotGroup:
    def __init__(self, group_id):
        self.group_id = group_id
        self.group_register()

    def group_register(self):
        """添加群组"""
        with MysqlDao() as db:
            res = db.query(
                'SELECT * FROM group_listener where uid=%s',
                [self.group_id]
            )
            if not res:
                res = db.update(
                    'INSERT INTO group_listener (uid, permission) VALUES (%s, %s)',
                    [self.group_id, '*']
                )
                if not res:
                    raise Exception()
