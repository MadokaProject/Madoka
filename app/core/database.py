from datetime import datetime
from pathlib import Path

from loguru import logger

from app.util.dao import MysqlDao
from app.util.tools import app_path


class Database:
    @classmethod
    def init(cls, root_dir: Path = None):
        """初始化数据表

        :param root_dir: 数据表文件所在目录
        """
        try:
            path = root_dir or app_path().joinpath('plugin')
            for file in sorted(path.rglob('database.sql')):
                with MysqlDao() as db:
                    for sql in file.read_text(encoding='utf-8').replace('\n', ' ').split(';'):
                        if sql := sql.strip():
                            db.update(sql)
            logger.success('初始化数据表成功')
        except Exception as e:
            logger.error('初始化数据表失败: ' + str(e))
            exit()

    @classmethod
    def update(cls, root_dir: Path = None):
        """更新数据表

        :param root_dir: 数据库文件所在目录
        """
        with MysqlDao() as db:
            path = root_dir or app_path().joinpath('plugin')
            for file in sorted(path.rglob('*.sql')):
                _ = file.parent.parent
                name = f'{_.parent.name}.{_.name}'
                if ret := db.query('SELECT time FROM update_time WHERE name = %s', [name]):
                    if file.name != 'database.sql' and file.name.split('.')[0] > ret[0][0]:
                        try:
                            for sql in file.read_text(encoding='utf-8').replace('\n', ' ').split(';'):
                                if sql := sql.strip():
                                    db.update(sql)
                            db.update(
                                'UPDATE update_time SET time = %s WHERE name = %s',
                                [file.name.split('.')[0], name]
                            )
                            logger.success(f'更新数据表成功 - {name}')
                        except Exception as e:
                            logger.error(f'更新数据表失败 - {name}: {e}')
                else:
                    db.update(
                        'INSERT INTO update_time (name, time) VALUES (%s, %s)',
                        [name, datetime.strftime(datetime.now(), '%Y%m%d-%H%M')]
                    )
