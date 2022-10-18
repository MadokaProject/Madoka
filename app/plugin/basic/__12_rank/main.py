from peewee import SQL, fn
from prettytable import PrettyTable

from app.plugin.basic.__01_sys.database.database import Msg as DBMsg
from app.util.alconna import Commander, Option
from app.util.graia import (
    Ariadne,
    Group,
    GroupMessage,
    Image,
    MessageChain,
    Plain,
    message,
)
from app.util.text2image import create_image

command = Commander("rank", "排行", Option("msg", help_text="显示群内成员发言排行榜"), help_text="查询各类榜单")


@command.parse("msg", events=[GroupMessage])
async def msg(app: Ariadne, sender: Group):
    members = await app.get_member_list(sender)
    group_user = {item.id: item.name for item in members}
    index = 1
    resp = MessageChain([Plain("群内发言排行：\r\n")])
    msg = PrettyTable()
    msg.field_names = ["序号", "群昵称", "发言条数"]
    for res in (
        DBMsg.select(DBMsg.qid, fn.COUNT(DBMsg.id).alias("num"))
        .where(DBMsg.uid == sender.id)
        .group_by(DBMsg.qid)
        .order_by(SQL("num").desc())
    ):
        if int(res.qid) not in group_user.keys():
            continue
        msg.add_row([index, group_user[int(res.qid)], res.num])
        index += 1
    msg.align = "r"
    msg.align["群昵称"] = "l"
    resp.extend(MessageChain([Image(data_bytes=await create_image(msg.get_string()))]))
    return message(resp).target(sender).send()
