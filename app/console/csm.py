from app.console.base import ConsoleController
from app.util.tools import isstartswith


class CSM(ConsoleController):
    entry = 'csm'
    brief_help = '群管'
    full_help = {
        'mute [GROUP] [QQ] [TIME]': '禁言指定群成员[TIME]分钟',
        'unmute [GROUP] [QQ]': '取消禁言指定群成员',
        'muteall [GROUP]': '开启全员禁言',
        'unmuteall [GROUP]': '关闭全员禁言'
    }

    async def process(self):
        if not self.param:
            self.print_help()
            return
        try:
            if isstartswith(self.param[0], 'mute', full_match=True):
                assert len(self.param) == 4 and self.param[1].isdigit() and self.param[2].isdigit() and self.param[3].isdigit()
                if await self.app.getGroup(int(self.param[1])):
                    if await self.app.getMember(int(self.param[1]), int(self.param[2])):
                        await self.app.muteMember(int(self.param[1]), int(self.param[2]), int(self.param[3]) * 60)
                        self.resp = '禁言成功!'
                    else:
                        self.resp = '未找到该群成员!'
                else:
                    self.resp = '未找到该群组!'
            elif isstartswith(self.param[0], 'unmute', full_match=True):
                assert len(self.param) == 3 and self.param[1].isdigit() and self.param[2].isdigit()
                if await self.app.getGroup(int(self.param[1])):
                    if await self.app.getMember(int(self.param[1]), int(self.param[2])):
                        await self.app.unmuteMember(int(self.param[1]), int(self.param[2]))
                        self.resp = '取消禁言成功!'
                    else:
                        self.resp = '未找到该群成员!'
                else:
                    self.resp = '未找到该群组!'
            elif isstartswith(self.param[0], ['muteall', 'unmuteall'], full_match=True):
                assert len(self.param) == 2 and self.param[1].isdigit()
                if await self.app.getGroup(int(self.param[1])):
                    if self.param[0] == 'muteall':
                        await self.app.muteAll(int(self.param[1]))
                        self.resp = '全员禁言成功!'
                    else:
                        await self.app.unmuteAll(int(self.param[1]))
                        self.resp = '取消全员禁言成功!'
                else:
                    self.resp = '未找到该群组'
            else:
                self.args_error()
        except PermissionError:
            self.exec_permission_error()
        except AssertionError:
            self.args_error()
        except Exception as e:
            self.unkown_error(e)
