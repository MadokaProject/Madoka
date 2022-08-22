from peewee import *

from app.util.dao import ORM


class Config(ORM):
    name = CharField()
    """配置名称"""
    uid = FixedCharField(max_length=10)
    """群组ID"""
    value = CharField(max_length=1024000)
    """配置值"""

    class Meta:
        table_name = 'config'
        indexes = (
            (('name', 'uid'), True),
        )
        primary_key = CompositeKey('name', 'uid')


class Msg(ORM):
    content = CharField(max_length=102400)
    """消息内容"""
    datetime = DateTimeField()
    """消息时间"""
    id = AutoField(primary_key=True)
    """序号"""
    qid = FixedCharField(max_length=12)
    """QQ号"""
    uid = FixedCharField(max_length=10)
    """群组ID"""

    class Meta:
        table_name = 'msg'


class UpdateTime(ORM):
    name = CharField(primary_key=True)
    """插件名"""
    time = FixedCharField(max_length=13)
    """更新时间"""

    class Meta:
        table_name = 'update_time'


Config.create_table()
Msg.create_table()
UpdateTime.create_table()
