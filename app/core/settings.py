from app.util.dao import MysqlDao

ACTIVE_GROUP = {}
with MysqlDao() as db:
    res = db.query('SELECT uid, permission FROM group_listener')
for (gid, permit) in res:
    ACTIVE_GROUP.update({
        int(gid): str(permit).split(',')
    })

ACTIVE_USER = {}
with MysqlDao() as db:
    res = db.query('SELECT uid, permission FROM friend_listener WHERE active=1')
for (qid, permit) in res:
    ACTIVE_USER.update({
        int(qid): str(permit).split(',')
    })

ADMIN_USER = []
with MysqlDao() as db:
    res = db.query('SELECT uid FROM friend_listener WHERE admin=1')
for (qid,) in res:
    ADMIN_USER.append(int(qid))
