from peewee import CharField, CompositeKey, FixedCharField, IntegerField

from app.util.dao import ORM


class McServer(ORM):
    default = IntegerField(default=0)
    """默认服务器"""
    delay = IntegerField(default=60)
    """监听延迟"""
    host = CharField()
    """服务器HOST"""
    listen = IntegerField(default=0)
    """是否监听"""
    port = FixedCharField(max_length=5)
    """服务器端口"""
    report = CharField(null=True)
    """回送QQ|群组"""

    class Meta:
        table_name = "mc_server"
        primary_key = CompositeKey("host", "port")


McServer.create_table()
