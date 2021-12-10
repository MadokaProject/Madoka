from loguru import logger

from app.plugin import *
from app.util.dao import MysqlDao


async def initDB():
    """初始化数据表"""

    async def initSysDB() -> None:
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
                "create table if not exists github( \
                    id int auto_increment comment '序号' primary key, \
                    repo varchar(50) not null comment '仓库', \
                    branch varchar(50) not null comment '分支', \
                    sha char(40) not null comment '记录')"
            )
            db.update(
                "create table if not exists github_config( \
                    id int auto_increment comment '序号' primary key, \
                    repo char(50) not null comment '仓库名', \
                    api char(110) not null comment 'api')"
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

    async def initPluginDB():
        for PluginDB in base.initDB.__subclasses__():
            """初始化插件数据表"""
            await PluginDB().process()

    try:
        await initSysDB()
        await initPluginDB()
        logger.success('初始化数据表成功')
        return True
    except Exception as e:
        logger.exception('初始化数据库失败：' + str(e))
