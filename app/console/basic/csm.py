from arclet.alconna import Alconna, Option, Args, Arpamar, exclusion

from app.console.base import ConsoleController
from app.core.commander import CommandDelegateManager

manager: CommandDelegateManager = CommandDelegateManager.get_instance()


@manager.register(
    entry='csm',
    brief_help='群管',
    alc=Alconna(
        command='csm',
        options=[
            Option(
                'mute',
                help_text='禁言指定群成员',
                args=Args['group': int, 'qq': int:0, 'time': int: 10],
            ),
            Option(
                'unmute',
                help_text='解除禁言指定群成员',
                args=Args['group': int, 'qq': int:0],
            ),
            Option('--all|-a', help_text='是否作用于全员'),
        ],
        help_text='群管助手',
        behaviors=[exclusion('options.mute', 'options.unmute')]
    )
)
async def process(self: ConsoleController, command: Arpamar):
    other_args = command.other_args
    all_ = True if command.options.get('all') else False
    if not command.options.get('mute') and not command.options.get('unmute'):
        return self.args_error()
    qq = other_args['qq']
    if not all_ and qq <= 0:
        return self.args_error()
    if (grp := (await self.app.getGroup(other_args['group']))) is None:
        return '未找到该群组'
    if (mbr := (await self.app.getMember(grp, qq))) is None and not all_:
        return '未找到该成员'
    try:
        if command.options.get('mute'):
            if all_:
                await self.app.muteAll(grp)
                return '全员禁言成功!'
            await self.app.muteMember(grp, mbr, other_args['time'] * 60)
            return '禁言成功!'
        elif command.options.get('unmute'):
            if all_:
                await self.app.unmuteAll(grp)
                return '取消全员禁言成功!'
            await self.app.unmuteMember(grp, mbr)
            return '解除禁言成功!'
        else:
            return self.args_error()
    except PermissionError:
        return self.exec_permission_error()
    except Exception as e:
        return self.unkown_error(e)
