import json

from loguru import logger
from peewee import OperationalError, fn

from app.core.config import Config
from app.plugin.basic.__01_sys.database.database import Config as DBConfig
from app.plugin.basic.__06_permission.database.database import Group as DBGroup
from app.plugin.basic.__06_permission.database.database import User as DBUser

try:
    config = Config()
    GROUP_PERM = {"OWNER": "群主", "ADMINISTRATOR": "管理员", "MEMBER": "普通成员"}
    """描述对象在群内的权限对应名称"""
    ACTIVE_GROUP = {int(_.uid): _.permission for _ in DBGroup.select().where(DBGroup.active == 1)}
    """监听群聊消息列表"""
    ACTIVE_USER = {int(_.uid): _.permission.split(",") for _ in DBUser.select().where(DBUser.active == 1)}
    ACTIVE_USER[config.MASTER_QQ] = "*"
    """监听好友消息列表"""
    BANNED_USER = [int(_.uid) for _ in DBUser.select().where(DBUser.level == 0)]
    """黑名单用户列表"""
    ADMIN_USER = [
        config.MASTER_QQ,
        *(int(_.uid) for _ in DBUser.select().where(DBUser.level >= 3) if int(_.uid) != config.MASTER_QQ),
    ]
    """具有超级管理权限以上QQ列表"""
    GROUP_ADMIN_USER = [int(_.uid) for _ in DBUser.select().where(DBUser.level == 2)]
    """具有群管理权限QQ列表"""
    CONFIG = {
        _.uid: {
            name: json.loads(value)
            for name, value in zip(
                _.group_name.replace("||,", "||").strip("||").split("||"),
                _.group_value.replace("||,", "||").strip("||").split("||"),
            )
        }
        for _ in DBConfig.select(
            DBConfig.uid,
            fn.GROUP_CONCAT(DBConfig.name, "||").alias("group_name"),
            fn.GROUP_CONCAT(DBConfig.value, "||").alias("group_value"),
        ).group_by(DBConfig.uid)
    }
    """存储在线配置

    eg: {group: {name: json.loads(value)}}
    """
    REPO = {k: v["repo"] for k, v in CONFIG.items() if "repo" in v}
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
    IntimacyLevel = (0, 10000, 15500, 20500, 26000, 31750, 37500, 43500, 49750, 56500)
    """描述各个好感度等级所需要的好感度"""
    IntimacyGet = (200, 350, 575, 912, 1418, 2177, 3315)
    """获取的好感度"""
except OperationalError as e:
    logger.error(e)
    exit(e)
