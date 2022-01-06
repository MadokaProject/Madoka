import json

import pymysql

from app.core.config import Config
from app.util.dao import MysqlDao

ACTIVE_GROUP = {}
"""监听群聊消息列表"""
ACTIVE_USER = {}
"""监听好友消息列表"""
BANNED_USER = []
"""黑名单用户列表"""
ADMIN_USER = [int(Config().MASTER_QQ)]
"""具有超级管理权限以上QQ列表"""
GROUP_ADMIN_USER = []
"""具有群管理权限QQ列表"""
LISTEN_MC_SERVER = []
"""MC服务器自动监听列表"""
CONFIG = {}
"""存储在线配置

eg: {group: {name: json.loads(value)}}
"""
try:
    with MysqlDao() as _db:
        _res = _db.query('SELECT uid, permission FROM `group` WHERE active=1')
    for _gid, _permit in _res:
        ACTIVE_GROUP.update({int(_gid): str(_permit).split(',')})

    with MysqlDao() as _db:
        _res = _db.query('SELECT uid, permission FROM user WHERE active=1')
    for _qid, _permit in _res:
        ACTIVE_USER.update({int(_qid): str(_permit).split(',')})

    with MysqlDao() as _db:
        _res = _db.query('SELECT uid FROM user WHERE level=0')
    for _qid in _res:
        BANNED_USER.append(int(_qid[0]))

    with MysqlDao() as _db:
        _res = _db.query('SELECT uid FROM user WHERE level>=3')
    for _qid in _res:
        if int(_qid[0]) not in ADMIN_USER:
            ADMIN_USER.append(int(_qid[0]))

    with MysqlDao() as _db:
        _res = _db.query('SELECT uid FROM user WHERE level=2')
    for _qid in _res:
        GROUP_ADMIN_USER.append(int(_qid[0]))

    with MysqlDao() as _db:
        _res = _db.query('SELECT ip,port,report,delay FROM mc_server WHERE listen=1')
    for (_ip, _port, _report, _delay) in _res:
        LISTEN_MC_SERVER.append(
            [[_ip, int(_port)], [i for i in str(_report).split(',')], _delay]
        )

    with MysqlDao() as _db:
        _res = _db.query('SELECT name, uid, value FROM config')
    for (_name, _uid, _value) in _res:
        if not CONFIG.__contains__(_uid):
            CONFIG.update({_uid: {}})
        CONFIG[_uid].update({
            _name: json.loads(_value)
        })
except pymysql.ProgrammingError:
    pass

REPO = {}
"""Github监听仓库

eg: {group: {name: {api:api, branch:branch}}}
"""
for _uid in CONFIG.keys():
    if CONFIG[_uid].__contains__('repo'):
        REPO.update({_uid: CONFIG[_uid]['repo']})

# 戳一戳记录
NUDGE_INFO = {}

# 游戏记录
MEMBER_RUNING_LIST = []
"""创建游戏人"""
GROUP_RUNING_LIST = []
"""在游戏的群"""
GROUP_GAME_PROCESS = {}
"""成员答题限次"""
