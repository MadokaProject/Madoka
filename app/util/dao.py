from typing import Union

from peewee import *

from app.core.config import Config

config: Config = Config()

db = {
    'sqlite': SqliteDatabase,
    'mysql': MySQLDatabase
}

database: Union[SqliteDatabase, MySQLDatabase] = db[config.DB_TYPE](config.DB_NAME, **config.DB_PARAMS)


class ORM(Model):
    class Meta:
        database = database
