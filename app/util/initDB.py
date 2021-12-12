import importlib
import os

from loguru import logger

from app.util.dao import MysqlDao
from app.util.tools import app_path


async def InitDB():
    """初始化数据表"""

    async def InitSysDB() -> None:
        """初始化系统数据表"""
        with MysqlDao() as db:
            """初始化系统数据表"""
            db.update(
                "create table if not exists msg( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(10) null comment '群号', \
                    qid char(12) null comment 'QQ', \
                    datetime datetime not null comment '时间', \
                    content varchar(800) not null comment '内容')"
            )
            db.update(
                "create table if not exists mc_server( \
                    ip char(15) not null comment 'IP', \
                    port char(5) not null comment '端口', \
                    report varchar(100) null, \
                    `default` int not null, \
                    listen int not null, \
                    delay int not null comment '超时时间')"
            )
            db.update(
                "create table if not exists config ( \
                    name varchar(30) not null comment '配置名', \
                    uid char(10) not null comment '群组', \
                    value varchar(500) not null comment '参数', \
                    primary key (name, uid))"
            )

    async def InitPluginDB():
        ignore = ["__init__.py", "__pycache__", "base.py"]
        for DB in os.listdir(os.path.join(app_path(), "plugin")):
            try:
                if DB not in ignore and not os.path.isdir(DB):
                    __DB = importlib.import_module(f"app.plugin.{DB.split('.')[0]}")
                    if hasattr(__DB, 'DB'):
                        await __DB.DB().process()
            except ModuleNotFoundError as __e:
                logger.error(f"初始化数据库失败: {DB} - {__e}")
                return False

    try:
        await InitSysDB()
        await InitPluginDB()
        logger.success('初始化数据表成功')
        return True
    except Exception as e:
        logger.error('初始化数据库失败: ' + str(e))
        return False
