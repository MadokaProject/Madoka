from typing import Union

from arclet.alconna import Alconna, Arpamar, CommandMeta, Option
from graia.ariadne import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.model import Friend, Group
from loguru import logger
from peewee import SQL, fn
from prettytable import PrettyTable

from app.core.commander import CommandDelegateManager
from app.plugin.basic.__01_sys.database.database import Msg as DBMsg
from app.util.phrases import args_error, print_help, unknown_error
from app.util.text2image import create_image

manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry="rank",
    brief_help="排行",
    alc=Alconna(
        "rank",
        Option("msg", help_text="显示群内成员发言排行榜"),
        meta=CommandMeta("查询各类榜单"),
    ),
)
async def process(app: Ariadne, sender: Union[Friend, Group], cmd: Arpamar, alc: Alconna):
    if not cmd.options:
        return await print_help(alc.get_help())
    try:
        if cmd.find("msg"):
            """发言榜"""
            if not isinstance(sender, Group):
                return MessageChain("请在群聊内发送该命令！")
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
            return resp
        return args_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()
