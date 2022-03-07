from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar

from app.console.base import ConsoleController
from app.core.command_manager import CommandManager


class CSM(ConsoleController):
    entry = 'csm'
    brief_help = '群管'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(
        command=entry,
        options=[
            Subcommand('mute', help_text='禁言指定群成员', args=Args['group': int, 'qq': int:0, 'time': int: 10],
                       options=[
                           Option('--all', alias='-a', help_text='开启全员禁言')
                       ]),
            Subcommand('unmute', help_text='解除禁言指定群成员', args=Args['group': int, 'qq': int:0], options=[
                Option('--all', alias='-a', help_text='关闭全员禁言')
            ])
        ],
        help_text='群管助手'
    ))
    async def process(self, command: Arpamar):
        subcommand = command.subcommands
        other_args = command.other_args
        try:
            if subcommand.__contains__('mute'):
                if other_args.__contains__('all'):
                    if await self.app.getGroup(other_args['group']):
                        await self.app.muteAll(other_args['group'])
                        return '全员禁言成功!'
                    else:
                        return '未找到该群组'
                elif other_args['qq'] != 0:
                    if await self.app.getGroup(other_args['group']):
                        if await self.app.getMember(other_args['group'], other_args['qq']):
                            await self.app.muteMember(other_args['group'], other_args['qq'], other_args['time'] * 60)
                            return '禁言成功!'
                        else:
                            return '未找到该群成员!'
                    else:
                        return '未找到该群组!'
                return self.args_error()
            elif subcommand.__contains__('unmute'):
                if other_args.__contains__('all'):
                    if await self.app.getGroup(other_args['group']):
                        await self.app.unmuteAll(other_args['group'])
                        return '取消全员禁言成功!'
                    else:
                        return '未找到该群组'
                elif other_args['qq'] != 0:
                    if await self.app.getGroup(other_args['group']):
                        if await self.app.getMember(other_args['group'], other_args['qq']):
                            await self.app.unmuteMember(other_args['group'], other_args['qq'])
                            return '禁言成功!'
                        else:
                            return '未找到该群成员!'
                    else:
                        return '未找到该群组!'
                return self.args_error()
            return self.args_error()
        except PermissionError:
            return self.exec_permission_error()
        except Exception as e:
            return self.unkown_error(e)
