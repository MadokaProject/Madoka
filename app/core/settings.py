import json

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

CONFIG = {}
with MysqlDao() as db:
    res = db.query('SELECT name, uid, value FROM config')
for (name, uid, value) in res:
    if not CONFIG.__contains__(uid):
        CONFIG.update({uid: {}})
    CONFIG[uid].update({
        name: json.loads(value)
    })
