from app.util.dao import MysqlDao


def save(group_id, member_id, content):
    """保存消息"""
    with MysqlDao() as db:
        res = db.update(
            'INSERT INTO msg (uid, qid, datetime, content) VALUES (%s, %s, NOW(), %s)',
            [group_id, member_id, content]
        )
        if not res:
            raise Exception()


def repeated(uid, qid, num):
    """复读判断"""
    with MysqlDao() as db:
        res = db.query(
            'SELECT content FROM msg WHERE uid=%s ORDER BY id DESC LIMIT %s',
            [uid, num]
        )
        if len(res) != num:
            raise Exception('消息数量不足, 无法进行复读判断')
        if res[0][0].startswith('[图片]'):
            return False
        for i in range(len(res) - 1):
            if res[i] != res[i + 1]:
                return False
        bot = db.query(
            'SELECT content FROM msg WHERE uid=%s AND qid=%s ORDER BY id DESC LIMIT %s',
            [uid, qid, 1]
        )
        if bot:
            if bot[0][0] == res[0][0]:
                return False
        return True
