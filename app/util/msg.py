from datetime import datetime

from graia.ariadne.message.chain import MessageChain

from app.plugin.basic.__01_sys.database.database import Msg as DBMsg


def save(group_id, member_id, content):
    """保存消息"""
    DBMsg.create(uid=group_id, qid=member_id, datetime=datetime.now(), content=content)


def repeated(uid, qid, num):
    """复读判断"""
    res = DBMsg.select().where(DBMsg.uid == uid).order_by(DBMsg.id.desc()).limit(num)
    if res.count() != num:
        return False
    content = MessageChain.from_persistent_string(res.get().content)
    if content.display.startswith("[图片]"):
        return False
    prev = None
    for msg in res:
        msg = MessageChain.from_persistent_string(msg.content)
        if prev and prev != msg:
            return False
        prev = msg
    bot = DBMsg.select().where(DBMsg.uid == uid, DBMsg.qid == qid).order_by(DBMsg.id.desc()).limit(1)
    return not bot or MessageChain.from_persistent_string(bot.get().content) != content
