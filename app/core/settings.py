import json

import pymysql

from app.core.config import Config
from app.util.dao import MysqlDao


def get_config(sql) -> list:
    try:
        with MysqlDao() as __db:
            return __db.query(sql)
    except pymysql.ProgrammingError:
        return []


config: Config = Config.get_instance()


GROUP_PERM = {
    'OWNER': '群主',
    'ADMINISTRATOR': '管理员',
    'MEMBER': '普通成员'
}
"""描述对象在群内的权限对应名称"""
ACTIVE_GROUP = {int(__gid): str(__permit).split(',') for __gid, __permit in
                get_config('SELECT uid, permission FROM `group` WHERE active=1')}
"""监听群聊消息列表"""
ACTIVE_USER = {config.MASTER_QQ: '*'}
"""监听好友消息列表"""
BANNED_USER = [int(__qid[0]) for __qid in get_config('SELECT uid FROM user WHERE level=0')]
"""黑名单用户列表"""
ADMIN_USER = [config.MASTER_QQ]
"""具有超级管理权限以上QQ列表"""
GROUP_ADMIN_USER = [int(__qid[0]) for __qid in get_config('SELECT uid FROM user WHERE level=2')]
"""具有群管理权限QQ列表"""
LISTEN_MC_SERVER = []
"""MC服务器自动监听列表"""
CONFIG = {}
"""存储在线配置

eg: {group: {name: json.loads(value)}}
"""
REPO = {}
"""Github监听仓库

eg: {group: {name: {api:api, branch:branch}}}
"""

# 戳一戳记录
NUDGE_INFO = {}

# 游戏记录
MEMBER_RUNING_LIST = []
"""创建游戏人"""
GROUP_RUNING_LIST = []
"""在游戏的群"""
GROUP_GAME_PROCESS = {}
"""成员答题限次"""

# 签到模块
IntimacyLevel = [0, 10000, 15500, 20500, 26000, 31750, 37500, 43500, 49750, 56500]
"""描述各个好感度等级所需要的好感度"""
IntimacyGet = [200, 350, 575, 912, 1418, 2177, 3315]
"""获取的好感度"""

for __qid, __permit in get_config('SELECT uid, permission FROM user WHERE active=1'):
    ACTIVE_USER.update({int(__qid): str(__permit).split(',')})

for __qid in get_config('SELECT uid FROM user WHERE level>=3'):
    if int(__qid[0]) not in ADMIN_USER:
        ADMIN_USER.append(int(__qid[0]))

for (__ip, __port, __report, __delay) in get_config('SELECT ip,port,report,delay FROM mc_server WHERE listen=1'):
    LISTEN_MC_SERVER.append(
        [[__ip, int(__port)], [i for i in str(__report).split(',')], __delay]
    )

for (__name, __uid, __value) in get_config('SELECT name, uid, value FROM config'):
    if not CONFIG.__contains__(__uid):
        CONFIG.update({__uid: {}})
    CONFIG[__uid].update({__name: json.loads(__value)})

for __uid in CONFIG.keys():
    if CONFIG[__uid].__contains__('repo'):
        REPO.update({__uid: CONFIG[__uid]['repo']})
