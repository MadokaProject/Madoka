import importlib
from datetime import datetime
from pathlib import Path

from loguru import logger

from app.core.config import Config
from app.plugin.basic.__01_sys.database.database import UpdateTime
from app.util.dao import database
from app.util.tools import app_path


def db_init(root_dir: Path = app_path().joinpath("plugin")):
    """初始化数据表

    :param root_dir: 数据表文件所在目录
    """
    try:
        for file in sorted(root_dir.rglob("database.py")):
            _ = file.parent.parent
            name = f"{_.parent.name}.{_.name}"
            importlib.import_module(f"app.plugin.{name}.database.database")
            if not UpdateTime.get_or_none(UpdateTime.name == name):
                UpdateTime.create(name=name, time=datetime.strftime(datetime.now(), "%Y%m%d-%H%M"))
        logger.success("初始化数据表成功")
    except Exception as e:
        logger.error(f"初始化数据表失败: {str(e)}")
        exit()


def db_update(root_dir: Path = app_path().joinpath("plugin")):
    """更新数据表

    :param root_dir: 数据库文件所在目录
    """
    for file in sorted(root_dir.rglob("*.sql")):
        _ = file.parent.parent
        name = f"{_.parent.name}.{_.name}"
        if file.name != "database.sql" and file.name.split(".")[0] > UpdateTime.get(UpdateTime.name == name).time:
            try:
                for sql in file.read_text(encoding="utf-8").replace("\n", " ").split(";"):
                    sql = sql.strip()
                    flag_mysql = sql.startswith("mysql:")
                    flag_sqlite = sql.startswith("sqlite:")
                    if Config.database.type == "mysql" and flag_mysql:
                        sql = sql.replace("mysql:", "")
                    elif Config.database.type == "sqlite" and flag_sqlite:
                        sql = sql.replace("sqlite:", "")
                    elif any([flag_mysql, flag_sqlite]):
                        continue
                    if sql := sql.strip():
                        database.execute_sql(sql, commit=True)
                UpdateTime.update(time=file.name.split(".")[0]).where(UpdateTime.name == name).execute()
                logger.success(f"更新数据表成功 - {name}")
            except Exception as e:
                logger.error(f"更新数据表失败 - {name}: {e}")
