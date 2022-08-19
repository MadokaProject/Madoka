import json
from typing import Union

from graia.ariadne.model import Group
from loguru import logger

from app.core.config import Config
from app.core.settings import CONFIG, ACTIVE_USER, ACTIVE_GROUP
from app.plugin.basic.__01_sys.database.database import Config as DBConfig
from app.plugin.basic.__06_permission.database.database import User as DBUser, Group as DBGroup


async def save_config(name: str, uid: Union[Group, int], value, model: str = None) -> None:
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
    try:
        if model in ['add', 'remove']:
            if res := DBConfig.get_or_none(name=name, uid=uid):
                params = json.loads(res.value)
                if model == 'add':
                    params.update(value)
                else:
                    params.pop(value)
    except Exception as e:
        logger.warning(e)
    DBConfig.replace(name=name, uid=uid, value=json.dumps(params)).execute()
    if uid not in CONFIG:
        CONFIG[uid] = {name: params}
    else:
        CONFIG[uid].update({name: params})


async def get_config(name: str, uid: Union[Group, int]) -> dict:
    """在线配置获取

    :param name: 配置名
    :param uid: 配置群组
    """
    if isinstance(uid, Group):
        uid = str(uid.id)
    else:
        uid = str(uid)
    if res := DBConfig.get_or_none(name=name, uid=uid):
        return json.loads(res.value)


async def set_plugin_switch(uid: Union[Group, int], perm: str) -> bool:
    """设置插件开关配置存储

    :param uid: 群组实例或QQ号
    :param perm: [插件名, -插件名, *, -]
    """
    try:
        if isinstance(uid, Group):
            if perm in ['*', '-']:
                DBGroup.update(permission=perm).where(DBGroup.uid == uid.id).execute()
                ACTIVE_GROUP[uid.id] = perm
                if perm == '-':
                    await set_plugin_switch(uid, 'plugin')
            else:
                res = [
                    i for i in DBGroup.get(DBGroup.uid == uid.id).permission.split(',')
                    if i not in [perm.strip('-'), f"-{perm.strip('-')}", '-']
                ]
                res.append(perm)
                ACTIVE_GROUP[uid.id] = res
                DBGroup.update(permission=','.join(res)).where(DBGroup.uid == uid.id).execute()
        else:
            config: Config = Config()
            if uid == config.MASTER_QQ:
                return False
            if perm in ['*', '-']:
                DBGroup.update(permission=perm).where(DBGroup.uid == uid).execute()
                ACTIVE_USER[uid] = perm
            else:
                res = [
                    i for i in DBUser.get(DBUser.uid == uid).permission.split(',')
                    if i not in (perm.strip('-'), f"-{perm.strip('-')}", '-')
                ]
                res.append(perm)
                ACTIVE_USER[uid] = res
                DBUser.update(permission=','.join(res)).where(DBUser.uid == uid).execute()
        return True
    except Exception as e:
        logger.error(f'没有这个群组/用户 - {e}')
        return False
