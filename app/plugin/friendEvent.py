from graia.application import MessageChain
from graia.application.message.elements.internal import Plain

from app.core.settings import NEW_FRIEND
from app.plugin.base import Plugin
from app.util.decorator import permission_required
from app.util.tools import isstartswith


class FriendEvent(Plugin):
    entry = ['.friend', '.好友']
    brief_help = '\r\n▶好友: friend'
    full_help = \
        '.friend\t仅管理可用！\r\n' \
        '.friend accept [QQ号]\t同意好友申请\r\n' \
        '.friend reject [QQ号}\t拒绝好友申请\r\n' \
        '.friend areject [QQ号]\t拒绝并不再接受该好友申请\r\n' \
        '.friend list\t查看好友申请列表'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'accept'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                print(self.msg[1], type(self.msg[1]))
                print(NEW_FRIEND)
                if NEW_FRIEND.__contains__(self.msg[1]):
                    await NEW_FRIEND[self.msg[1]].accept()
                    NEW_FRIEND.pop(self.msg[1])
                    self.resp = MessageChain.create([
                        Plain('同意成功！')
                    ])
                else:
                    self.resp = MessageChain.create([
                        Plain('无该QQ申请记录！')
                    ])
            elif isstartswith(self.msg[0], 'reject'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if NEW_FRIEND.__contains__(self.msg[1]):
                    await NEW_FRIEND[self.msg[1]].reject()
                    NEW_FRIEND.pop(self.msg[1])
                    self.resp = MessageChain.create([
                        Plain('拒绝成功！')
                    ])
                else:
                    self.resp = MessageChain.create([
                        Plain('无该QQ申请记录！')
                    ])
            elif isstartswith(self.msg[0], 'areject'):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if NEW_FRIEND.__contains__(self.msg[1]):
                    await NEW_FRIEND[self.msg[1]].rejectAndBlock()
                    NEW_FRIEND.pop(self.msg[1])
                    self.resp = MessageChain.create([
                        Plain('已拒绝并不再接受申请！')
                    ])
                else:
                    self.resp = MessageChain.create([
                        Plain('无该QQ申请记录')
                    ])
            elif isstartswith(self.msg[0], 'list'):
                self.resp = MessageChain.create([
                    Plain('\n'.join(f'{index + 1}: {qid}' for index, qid in
                                    enumerate(NEW_FRIEND.keys())) if NEW_FRIEND else '暂无QQ申请记录')
                ])
            else:
                self.args_error()
                return
        except PermissionError as e:
            print(e)
            self.exec_permission_error()
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            print(e)
            self.unkown_error()
