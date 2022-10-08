from app.core.app import AppCore
from app.core.config import Config
from app.util.graia import Ariadne, message
from app.util.online_config import get_config

app: Ariadne = AppCore().get_app()
config: Config = Config()


async def online_notice():
    """上线提醒"""
    if config.ONLINE:
        group_list = await app.get_group_list()
        for group in group_list:
            if await get_config("online_notice", group.id):
                message(f"{config.BOT_NAME}打卡上班啦！").target(group).send()


async def offline_notice():
    """下线提醒"""
    if config.ONLINE:
        message("正在关闭").target(config.MASTER_QQ).send()
