from arclet.alconna import Alconna, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.core.initDB import InitDB
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.dao import MysqlDao
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config

manager: CommandDelegateManager = CommandDelegateManager.get_instance()
database: InitDB = InitDB.get_instance()
configs = {'禁言退群': 'bot_mute_event', '上线通知': 'online_notice'}


@permission_required(level=Permission.MASTER)
@manager.register(
    entry='sys',
    brief_help='系统',
    hidden=True,
    alc=Alconna(
        headers=manager.headers,
        command='sys',
        options=[
            Option('禁言退群', help_text='设置机器人禁言是否退群', args=Args['bool': bool]),
            Option('上线通知', help_text='设置机器人上线是否通知该群', args=Args['bool': bool])
        ],
        help_text='系统设置: 仅主人可用!'
    )
)
async def process(self: Plugin, command: Arpamar, alc: Alconna):
    options = command.options
    if not options:
        return await self.print_help(alc.get_help())
    try:
        if not hasattr(self, 'group'):
            return MessageChain.create([Plain('请在群聊内使用该命令!')])
        config_name = configs[list(options.keys())[0]]
        if await save_config(config_name, self.group.id, command.query('bool')):
            return MessageChain.create([Plain('开启成功！' if command.query('bool') else '关闭成功！')])
    except Exception as e:
        logger.exception(e)
        return self.unkown_error()


@database()
def init_db():
    with MysqlDao() as db:
        """初始化系统数据表"""
        db.update(
            "create table if not exists msg( \
                id int auto_increment comment '序号' primary key, \
                uid char(10) null comment '群号', \
                qid char(12) null comment 'QQ', \
                datetime datetime not null comment '时间', \
                content varchar(800) not null comment '内容')"
        )
        db.update(
            "create table if not exists mc_server( \
                ip char(15) not null comment 'IP', \
                port char(5) not null comment '端口', \
                report varchar(100) null, \
                `default` int not null, \
                listen int not null, \
                delay int not null comment '超时时间')"
        )
        db.update(
            "create table if not exists config ( \
                name varchar(256) not null comment '配置名', \
                uid char(10) not null comment '群组', \
                value varchar(500) not null comment '参数', \
                primary key (name, uid))"
        )
