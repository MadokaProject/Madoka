from typing import Union

from peewee import Model, MySQLDatabase, SqliteDatabase

from app.core.config import DB_PARAMS, Config

db = {"sqlite": SqliteDatabase, "mysql": MySQLDatabase}

database: Union[SqliteDatabase, MySQLDatabase] = db[Config.database.type](Config.database.name, **DB_PARAMS)


class ORM(Model):
    class Meta:
        database = database
