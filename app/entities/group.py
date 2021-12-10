from app.util.dao import MysqlDao


class BotGroup:
    def __init__(self, group_id, active=0):
        self.group_id = group_id
        self.active = active
        self.group_register()

    def group_register(self):
        """注册群组"""
        with MysqlDao() as db:
            res = db.query(
                "SELECT COUNT(*) FROM `group` WHERE uid=%s",
                [self.group_id]
            )
            if not res[0][0]:
                res = db.update(
                    "INSERT INTO `group` (uid, permission, active) VALUES (%s, %s, %s)",
                    [self.group_id, '*', self.active]
                )
                if not res:
                    raise Exception()
            elif self.active == 1:
                res = db.update(
                    "UPDATE `group` SET active=%s WHERE uid=%s", [self.active, self.group_id]
                )
                if not res:
                    raise Exception()
