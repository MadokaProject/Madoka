import json

from app.core.settings import CONFIG
from app.util.dao import MysqlDao


def save_config(name: str, uid, value, model: str = None) -> bool:
    """在线配置存储
    :param name: 配置名
    :param uid: 配置群组
    :param value: 配置项
    :param model: 模式 [add: 添加, remove: 删除], 若不指定则为覆盖模式
    """
    params = value
    uid = str(uid)
    with MysqlDao() as db:
        try:
            if model in ['add', 'remove']:
                res = db.query('SELECT value FROM config WHERE name=%s and uid=%s', [name, uid])
                if res:
                    params = json.loads(res[0][0])
                    if model == 'add':
                        params.update(value)
                    else:
                        params.pop(value)
        except Exception:
            pass
        if db.update('REPLACE INTO config(name, uid, value) VALUES (%s, %s, %s)',
                     [name, uid, json.dumps(params)]):
            if not CONFIG.__contains__(uid):
                CONFIG.update({uid: {}})
            CONFIG[uid].update({name: params})
            return True
    return False


def get_config(name: str, uid) -> dict:
    """在线配置获取
    :param name: 配置名
    :param uid: 配置群组
    """
    uid = str(uid)
    with MysqlDao() as db:
        res = db.query('SELECT value FROM config WHERE name=%s and uid=%s', [name, uid])
        if res:
            print(res[0])
            return json.loads(res[0][0])
