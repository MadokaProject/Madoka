from app.console.base import ConsoleController
from app.util.tools import isstartswith, command_parse


class CSM(ConsoleController):
    entry = 'csm'
    brief_help = '群管'
    full_help = {
        "mute": {
            "禁言指定群成员": '',
            "-g, --group": "指定群",
            "-q, --qq": "指定群成员",
            "-t, --time": "禁言时间(分钟)",
            "all": {
                "全体禁言": '',
                "-g, --group": "指定群"
            }
        },
        "unmute": {
            "取消禁言指定群成员": '',
            "-g, --group": "指定群",
            "-q, --qq": "指定群成员",
            "all": {
                "取消全体禁言": '',
                "-g, --group": "指定群"
            }
        }
    }

    async def process(self):
        if not self.param:
            self.print_help()
            return
        try:
            if isstartswith(self.param[0], 'mute', full_match=True):
                commands = command_parse(self.param[1:])
                if commands.__contains__('all'):
                    for i in [['-g', '--group']]:
                        for j in i:
                            if commands['all'].__contains__(j):
                                group = int(commands['all'][j])
                                break
                        else:
                            raise KeyError(i)
                    if await self.app.getGroup(group):
                        await self.app.muteAll(group)
                        self.resp = '全员禁言成功!'
                    else:
                        self.resp = '未找到该群组'
                else:
                    param = []
                    for i in [['-g', '--group'], ['-q', '-qq'], ['-t', '--time']]:
                        for j in i:
                            if commands.__contains__(j):
                                param.append(int(commands[j]))
                                break
                        else:
                            raise KeyError(i)
                    if await self.app.getGroup(param[0]):
                        if await self.app.getMember(param[0], param[1]):
                            await self.app.muteMember(param[0], param[1], param[2] * 60)
                            self.resp = '禁言成功!'
                        else:
                            self.resp = '未找到该群成员!'
                    else:
                        self.resp = '未找到该群组!'
            elif isstartswith(self.param[0], 'unmute', full_match=True):
                commands = command_parse(self.param[1:])
                if commands.__contains__('all'):
                    for i in [['-g', '--group']]:
                        for j in i:
                            if commands['all'].__contains__(j):
                                group = int(commands['all'][j])
                                break
                        else:
                            raise KeyError(i)
                    if await self.app.getGroup(group):
                        await self.app.unmuteAll(group)
                        self.resp = '取消全员禁言成功!'
                    else:
                        self.resp = '未找到该群组'
                else:
                    param = []
                    for i in [['-g', '--group'], ['-q', '-qq']]:
                        for j in i:
                            if commands.__contains__(j):
                                param.append(int(commands[j]))
                                break
                        else:
                            raise KeyError(i)
                    if await self.app.getGroup(param[0]):
                        if await self.app.getMember(param[0], param[1]):
                            await self.app.unmuteMember(param[0], param[1])
                            self.resp = '禁言成功!'
                        else:
                            self.resp = '未找到该群成员!'
                    else:
                        self.resp = '未找到该群组!'
            else:
                self.args_error()
        except PermissionError:
            self.exec_permission_error()
        except KeyError:
            self.args_error('too few arguments')
        except AssertionError:
            self.args_error()
        except Exception as e:
            self.unkown_error(e)
