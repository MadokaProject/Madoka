from app.util.dao import MysqlDao


def save(group_id, member_id, content):
    with MysqlDao() as db:
        res = db.update(
            'INSERT INTO msg (uid, qid, datetime, content) VALUES (%s, %s, NOW(), %s)',
            [group_id, member_id, content]
        )
        if not res:
            raise Exception()
