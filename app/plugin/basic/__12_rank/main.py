from typing import Union

from arclet.alconna import Alconna, Option, Arpamar
from graia.ariadne import Ariadne
from graia.ariadne.model import Friend, Group
from loguru import logger
from prettytable import PrettyTable

from app.core.commander import CommandDelegateManager
from app.util.dao import MysqlDao
from app.util.phrases import *
from app.util.text2image import create_image

manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry='rank',
    brief_help='排行',
    alc=Alconna(
        headers=manager.headers,
        command='rank',
        options=[
            Option('msg', help_text='显示群内成员发言排行榜')
        ],
        help_text='查询各类榜单'
    )
)
async def process(app: Ariadne, sender: Union[Friend, Group], command: Arpamar, alc: Alconna):
    options = command.options
    if not options:
        return await print_help(alc.get_help())
    try:
        if 'msg' in options:
            """发言榜"""
            if not isinstance(sender, Group):
                return MessageChain('请在群聊内发送该命令！')
            with MysqlDao() as db:
                res = db.query(
                    "SELECT qid, count(qid) FROM msg WHERE uid=%s GROUP BY qid ORDER BY count(qid) DESC",
                    [sender.id]
                )
                members = await app.get_member_list(sender)
                group_user = {item.id: item.name for item in members}
                index = 1
                resp = MessageChain([Plain('群内发言排行：\r\n')])
                msg = PrettyTable()
                msg.field_names = ['序号', '群昵称', '发言条数']
                for qid, num in res:
                    if int(qid) not in group_user.keys():
                        continue
                    msg.add_row([index, group_user[int(qid)], num])
                    index += 1
                msg.align = 'r'
                msg.align['群昵称'] = 'l'
                resp.extend(MessageChain([
                    Image(data_bytes=await create_image(msg.get_string()))
                ]))
                return resp
        return args_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()
