from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.am', '.account', '.账号管理']
    brief_help = '账号管理'
    full_help = {
        '仅主人可用': '',
        '列出群组, gl': '列出机器人的群组列表',
        '列出好友, ul': '列出机器人的好友列表',
        '退出群组, dg': {
            '退出指定群组': '',
            '[num]': '群号码'
        },
        '删除好友, du': {
            '删除指定好友': '',
            '[num]': 'QQ号码'
        }
    }
    hidden = True

    @permission_required(level=Permission.MASTER)
    async def process(self):
        if not self.msg:
            await self.print_help()
            return
        try:
            if isstartswith(self.msg[0], ['列出群组', 'gl']):
                group_list = await self.app.getGroupList()
                self.resp = MessageChain.create([
                    Plain('\r\n'.join(f'群ID：{str(group.id).ljust(14)}群名：{group.name}' for group in group_list))
                ])
            elif isstartswith(self.msg[0], ['列出好友', 'ul']):
                friend_list = await self.app.getFriendList()
                self.resp = MessageChain.create([
                    Plain('\r\n'.join(
                        f'好友ID：{str(friend.id).ljust(14)}好友昵称：{str(friend.nickname)}' for friend in friend_list))
                ])
            elif isstartswith(self.msg[0], ['退出群组', 'dg']):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if await self.app.getGroup(int(self.msg[1])):
                    await self.app.quitGroup(int(self.msg[1]))
                    msg = '成功退出该群组！'
                else:
                    msg = '没有找到该群组！'
                self.resp = MessageChain.create([Plain(msg)])
            elif isstartswith(self.msg[0], ['删除好友', 'du']):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if await self.app.getFriend(int(self.msg[1])):
                    await self.app.deleteFriend(int(self.msg[1]))
                    msg = '成功删除该好友！'
                else:
                    msg = '没有找到该好友！'
                self.resp = MessageChain.create([Plain(msg)])
            else:
                self.args_error()
                return
        except AssertionError:
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
