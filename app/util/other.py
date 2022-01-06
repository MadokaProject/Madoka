from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.core.config import Config
from app.util.onlineConfig import get_config


async def online_notice(app: Ariadne, config: Config):
    """上线提醒"""
    if config.ONLINE:
        group_list = await app.getGroupList()
        for group in group_list:
            if await get_config('online_notice', group.id):
                await app.sendGroupMessage(group, MessageChain.create([Plain(f"{config.BOT_NAME}打卡上班啦！")]))


async def offline_notice(app: Ariadne, config: Config):
    """下线提醒"""
    if config.ONLINE:
        await app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([Plain("正在关闭")]))
