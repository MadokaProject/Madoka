from app.util.dao import MysqlDao

ACTIVE_GROUP = {}
ID_TO_GROUP = {
    1: 771414803
}
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

REPO = {}
with MysqlDao() as db:
    res = db.query('SELECT repo, api FROM github_config')
for (repo, api) in res:
    REPO.update({
        str(repo): str(api)
    })

LISTEN_MC_SERVER = []
with MysqlDao() as db:
    res = db.query('SELECT ip,port,report,delay FROM mc_server WHERE listen=1')
for (ip, port, report, delay) in res:
    LISTEN_MC_SERVER.append(
        [[ip, int(port)], [i for i in str(report).split(',')], delay]
    )
