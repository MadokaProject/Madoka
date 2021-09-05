import json

from app.util.dao import MysqlDao

ACTIVE_GROUP = {}
"""监听群聊消息列表"""
with MysqlDao() as db:
    res = db.query('SELECT uid, permission FROM `group` WHERE active=1')
for (gid, permit) in res:
    ACTIVE_GROUP.update({
        int(gid): str(permit).split(',')
    })

ACTIVE_USER = {}
"""监听好友消息列表"""
with MysqlDao() as db:
    res = db.query('SELECT uid FROM user WHERE active=1')
for (qid,) in res:
    ACTIVE_USER.update({
        int(qid): '*'
    })

ADMIN_USER = []
"""具有管理权限QQ列表"""
with MysqlDao() as db:
    res = db.query('SELECT uid FROM user WHERE admin=1')
for (qid,) in res:
    ADMIN_USER.append(int(qid))

REPO = {}
"""Github监听仓库"""
with MysqlDao() as db:
    res = db.query('SELECT repo, api FROM github_config')
for (repo, api) in res:
    REPO.update({
        str(repo): str(api)
    })

LISTEN_MC_SERVER = []
"""MC服务器自动监听列表"""
with MysqlDao() as db:
    res = db.query('SELECT ip,port,report,delay FROM mc_server WHERE listen=1')
for (ip, port, report, delay) in res:
    LISTEN_MC_SERVER.append(
        [[ip, int(port)], [i for i in str(report).split(',')], delay]
    )

CONFIG = {}
"""存储在线配置"""
with MysqlDao() as db:
    res = db.query('SELECT name, uid, value FROM config')
for (name, uid, value) in res:
    if not CONFIG.__contains__(uid):
        CONFIG.update({uid: {}})
    CONFIG[uid].update({
        name: json.loads(value)
    })

NEW_FRIEND = {}
"""存储好友申请实例"""
