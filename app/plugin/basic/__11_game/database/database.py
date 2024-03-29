from peewee import CompositeKey, DateField, FixedCharField, IntegerField

from app.util.dao import ORM


class Game(ORM):
    auto_signin = IntegerField(default=0, null=True)
    """自动签到"""
    coin = IntegerField(null=True)
    """今日获得货币"""
    coins = IntegerField(default=0)
    """总获得货币"""
    consecutive_days = IntegerField(default=0)
    """连续签到天数"""
    english_answer = IntegerField(default=0, null=True)
    """英语答题榜"""
    intimacy = IntegerField(default=0)
    """好感度"""
    intimacy_level = IntegerField(default=0)
    """好感度等级"""
    last_signin_time = DateField(null=True)
    """最后签到时间"""
    qid = FixedCharField(max_length=12)
    """QQ号"""
    total_days = IntegerField(default=0)
    """签到总天数"""
    uuid = FixedCharField(max_length=36)
    """UUID"""

    class Meta:
        table_name = "game"
        indexes = ((("uuid", "qid"), True),)
        primary_key = CompositeKey("qid", "uuid")


Game.create_table()
