from arclet.alconna import Alconna, Subcommand, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from loguru import logger
from prettytable import PrettyTable

from app.core.command_manager import CommandManager
from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.text2image import create_image


class Module(Plugin):
    entry = 'rank'
    brief_help = '排行'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('msg', help_text='显示群内成员发言排行榜')
        ],
        help_text='查询各类榜单'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        if not subcommand:
            return await self.print_help(alc.get_help())
        try:
            if subcommand.__contains__('msg'):
                """发言榜"""
                with MysqlDao() as db:
                    res = db.query(
                        "SELECT qid, count(qid) FROM msg WHERE uid=%s GROUP BY qid ORDER BY count(qid) DESC",
                        [self.group.id]
                    )
                    members = await self.app.getMemberList(self.group.id)
                    group_user = {item.id: item.name for item in members}
                    index = 1
                    resp = MessageChain.create([Plain('群内发言排行：\r\n')])
                    msg = PrettyTable()
                    msg.field_names = ['序号', '群昵称', '发言条数']
                    for qid, num in res:
                        if int(qid) not in group_user.keys():
                            continue
                        msg.add_row([index, group_user[int(qid)], num])
                        index += 1
                    msg.align = 'r'
                    msg.align['群昵称'] = 'l'
                    resp.extend(MessageChain.create([
                        Image(data_bytes=await create_image(msg.get_string()))
                    ]))
                    return resp
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()
