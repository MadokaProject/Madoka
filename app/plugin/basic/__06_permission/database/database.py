from peewee import *

from app.util.dao import ORM


class User(ORM):
    active = IntegerField(null=True)
    """激活状态"""
    id = AutoField(primary_key=True)
    """ID"""
    level = IntegerField(constraints=[SQL("DEFAULT 1")])
    """权限等级"""
    permission = CharField(constraints=[SQL("DEFAULT '*'")])
    """插件许可"""
    uid = FixedCharField(max_length=12)
    """QQ号"""

    class Meta:
        table_name = 'user'


class Group(ORM):
    active = IntegerField()
    """激活状态"""
    permission = CharField(max_length=512)
    """插件许可"""
    uid = FixedCharField(max_length=12, primary_key=True)
    """群组ID"""

    class Meta:
        table_name = 'group'


User.create_table()
Group.create_table()
