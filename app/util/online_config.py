import json
from typing import Union

from graia.ariadne.model import Group
from loguru import logger

from app.core.config import Config
from app.core.settings import CONFIG, ACTIVE_USER, ACTIVE_GROUP
from app.util.dao import MysqlDao


async def save_config(name: str, uid: Union[Group, int], value, model: str = None) -> bool:
    """在线配置存储

    :param name: 配置名
    :param uid: 配置群组
    :param value: 配置项
    :param model: 模式 [add: 添加, remove: 删除], 若不指定则为覆盖模式
    """
    params = value
    if isinstance(uid, Group):
        uid = str(uid.id)
    else:
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
        except Exception as e:
            logger.warning(e)
        if db.update('REPLACE INTO config(name, uid, value) VALUES (%s, %s, %s)',
                     [name, uid, json.dumps(params)]):
            if not CONFIG.__contains__(uid):
                CONFIG.update({uid: {}})
            CONFIG[uid].update({name: params})
            return True
    return False


async def get_config(name: str, uid: Union[Group, int]) -> dict:
    """在线配置获取

    :param name: 配置名
    :param uid: 配置群组
    """
    if isinstance(uid, Group):
        uid = str(uid.id)
    else:
        uid = str(uid)
    with MysqlDao() as db:
        res = db.query('SELECT value FROM config WHERE name=%s and uid=%s', [name, uid])
        if res:
            return json.loads(res[0][0])


async def set_plugin_switch(uid: Union[Group, int], perm: str) -> bool:
    """设置插件开关配置存储

    :param uid: 群组实例或QQ号
    :param perm: [插件名, -插件名, *, -]
    """
    try:
        if isinstance(uid, Group):
            with MysqlDao() as db:
                if perm in ['*', '-']:
                    db.update('UPDATE `group` SET permission=%s WHERE uid=%s', [perm, uid.id])
                    ACTIVE_GROUP[uid.id] = perm
                    if perm == '-':
                        await set_plugin_switch(uid, 'plugin')
                else:
                    res = str(db.query('SELECT permission FROM `group` WHERE uid=%s', [uid.id])[0][0]).split(',')
                    res = [i for i in res if i not in [perm.strip('-'), f"-{perm.strip('-')}", '-']]
                    res.append(perm)
                    ACTIVE_GROUP[uid.id] = res
                    db.update('UPDATE `group` SET permission=%s WHERE uid=%s', [','.join(f'{i}' for i in res), uid.id])
        else:
            config: Config = Config()
            if uid == config.MASTER_QQ:
                return False
            with MysqlDao() as db:
                if perm in ['*', '-']:
                    db.update('UPDATE user SET permission=%s WHERE uid=%s', [perm, uid])
                    ACTIVE_USER[uid] = perm
                else:
                    res = str(db.query('SELECT permission FROM user WHERE uid=%s', [uid])[0][0]).split(',')
                    res = [i for i in res if i not in [perm.strip('-'), f"-{perm.strip('-')}", '-']]
                    res.append(perm)
                    ACTIVE_USER[uid] = res
                    db.update('UPDATE user SET permission=%s WHERE uid=%s', [','.join(f'{i}' for i in res), uid])
        return True
    except Exception as e:
        logger.error(f'没有这个群组/用户 - {e}')
        return False
