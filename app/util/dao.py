import pymysql

from app.core.config import Config


class MysqlDao:
    def __enter__(self):
        try:
            config = Config.get_instance()
            self.db = pymysql.connect(
                host=config.MYSQL_HOST,
                port=config.MYSQL_PORT,
                user=config.MYSQL_USER,
                password=config.MYSQL_PWD,
                database=config.MYSQL_DATABASE
            )
            self.cur = self.db.cursor()
            return self
        except Exception as e:
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.db.close()

    def query(self, sql, args=None):
        try:
            self.cur.execute(sql, args=args)
            query_result = self.cur.fetchall()
        except Exception as e:
            raise e
        return query_result

    def update(self, sql, args=None):
        try:
            effect_rows = self.cur.execute(sql, args=args)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        return effect_rows
