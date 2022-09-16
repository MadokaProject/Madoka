from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.core.config import Config
from app.util.online_config import get_config


async def online_notice(app: Ariadne, config: Config):
    """上线提醒"""
    if config.ONLINE:
        group_list = await app.get_group_list()
        for group in group_list:
            if await get_config("online_notice", group.id):
                await app.send_group_message(group, MessageChain([Plain(f"{config.BOT_NAME}打卡上班啦！")]))


async def offline_notice(app: Ariadne, config: Config):
    """下线提醒"""
    if config.ONLINE:
        await app.send_friend_message(config.MASTER_QQ, MessageChain([Plain("正在关闭")]))
