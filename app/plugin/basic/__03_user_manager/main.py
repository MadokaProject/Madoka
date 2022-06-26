from arclet.alconna import Alconna, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required

manager: CommandDelegateManager = CommandDelegateManager.get_instance()


@permission_required(level=Permission.MASTER)
@manager.register(
    entry='am',
    brief_help='账号管理',
    hidden=True,
    alc=Alconna(
        headers=manager.headers,
        command='am',
        options=[
            Option('list', Args["type", ["friend", "group", "f", "g"]], help_text='列出好友、群列表'),
            Option('delete', Args["type", ["friend", "group", "f", "g"]]["id", int], help_text='删除好友、群')
        ],
        help_text='账号管理'
    )
)
async def process(self: Plugin, command: Arpamar, alc: Alconna):
    options = command.options
    if not options:
        return await self.print_help(alc.get_help())
    try:
        if list_ := options.get("list"):
            rs_type = list_.get("type")
            if rs_type in ["friend", "f"]:
                friend_list = await self.app.get_friend_list()
                return MessageChain([
                    Plain('\r\n'.join(
                        f'好友ID：{str(friend.id).ljust(14)}好友昵称：{str(friend.nickname)}' for friend in friend_list))
                ])
            elif rs_type in ["group", "g"]:
                group_list = await self.app.get_group_list()
                return MessageChain([
                    Plain('\r\n'.join(f'群ID：{str(group.id).ljust(14)}群名：{group.name}' for group in group_list))
                ])
        elif delete_ := options.get("delete"):
            rs_type = delete_.get("type")
            target_id = delete_.get("id")
            if rs_type in ["friend", "f"]:
                if await self.app.get_friend(target_id):
                    await self.app.delete_friend(target_id)
                    msg = '成功删除该好友！'
                else:
                    msg = '没有找到该好友！'
                return MessageChain([Plain(msg)])
            elif rs_type in ["group", "g"]:
                if await self.app.get_group(target_id):
                    await self.app.quit_group(target_id)
                    msg = '成功退出该群组！'
                else:
                    msg = '没有找到该群组！'
                return MessageChain([Plain(msg)])
        return self.args_error()
    except Exception as e:
        logger.exception(e)
        return self.unkown_error()
