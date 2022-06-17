from arclet.alconna import Alconna, Option, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from loguru import logger
from prettytable import PrettyTable

from app.core.commander import CommandDelegateManager
from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.text2image import create_image

manager: CommandDelegateManager = CommandDelegateManager.get_instance()


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
async def process(self: Plugin, command: Arpamar, alc: Alconna):
    options = command.options
    if not options:
        return await self.print_help(alc.get_help())
    try:
        if 'msg' in options:
            """发言榜"""
            if not hasattr(self, 'group'):
                return MessageChain('请在群聊内发送该命令！')
            with MysqlDao() as db:
                res = db.query(
                    "SELECT qid, count(qid) FROM msg WHERE uid=%s GROUP BY qid ORDER BY count(qid) DESC",
                    [self.group.id]
                )
                members = await self.app.get_member_list(self.group.id)
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
        return self.args_error()
    except Exception as e:
        logger.exception(e)
        return self.unkown_error()
