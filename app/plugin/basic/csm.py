from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, At
from loguru import logger

from app.core.command_manager import CommandManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config


class Module(Plugin):
    entry = 'csm'
    brief_help = '群管'
    manager: CommandManager = CommandManager.get_command_instance()

    @permission_required(level=Permission.GROUP_ADMIN)
    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('status', args=Args['status': bool], help_text='开关群管'),
            Subcommand('kick', args=Args['at': At], help_text='踢出指定群成员'),
            Subcommand('revoke', args=Args['id': int], help_text='撤回消息, id=消息ID, 自最后一条消息起算'),
            Subcommand('mute', args=Args['at': At: ''], help_text='禁言指定群成员', options=[
                Option('--time', alias='-t', args=Args['time': int:10], help_text='禁言时间(分)'),
                Option('--all', alias='-a', help_text='开启全员禁言')
            ]),
            Subcommand('unmute', args=Args['at': At: ''], help_text='取消禁言指定群成员', options=[
                Option('--all', alias='-a', help_text='关闭全员禁言')
            ]),
            Subcommand('func', args=Args['status': bool], help_text='功能开关', options=[
                Option('--card', alias='-C', help_text='成员名片修改通知'),
                Option('--flash', alias='-F', help_text='闪照识别'),
                Option('--kick', alias='-K', help_text='成员被踢通知'),
                Option('--quit', alias='-Q', help_text='成员退群通知')
            ]),
            Subcommand('刷屏检测', args=Args['time': int, 'mute_time': int, 'reply': str],
                       help_text='检测time内的3条消息是否刷屏; <time>: 秒, <mute_time>: 分钟, <reply>: 回复消息'),
            Subcommand('重复消息', args=Args['time': int, 'mute_time': int, 'reply': str],
                       help_text='检测time内的3条消息是否重复; <time>: 秒, <mute_time>: 分钟, <reply>: 回复消息'),
            Subcommand('超长消息', args=Args['len': int, 'mute_time': int, 'reply': str],
                       help_text='检测单消息是否超出设定的长度; <len>: 文本长度, <mute_time>: 分钟, <reply>: 回复消息'),
        ],
        help_text='群管助手'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        other_args = command.other_args
        if not subcommand:
            return await self.print_help(alc.get_help())
        try:
            if not hasattr(self, 'group'):
                return MessageChain.create([Plain('请在群聊内使用该命令!')])
            if subcommand.__contains__('status'):
                if await save_config('status', self.group.id, other_args['status']):
                    return MessageChain.create([Plain('开启成功!' if other_args['status'] else '关闭成功!')])
            elif subcommand.__contains__('kick'):
                await self.app.kickMember(self.group, other_args['at'].target)
                return MessageChain.create([Plain('飞机票快递成功!')])
            elif subcommand.__contains__('revoke'):
                await self.app.recallMessage(self.message[Source][0].id - other_args['id'])
                return MessageChain.create([Plain('消息撤回成功!')])
            elif subcommand.__contains__('mute'):
                if subcommand['mute'].__contains__('all'):
                    await self.app.muteAll(self.group.id)
                    return MessageChain.create([Plain('开启全员禁言成功!')])
                elif isinstance(other_args['at'], At):
                    time = other_args['time'] if other_args.__contains__('time') else 10
                    await self.app.muteMember(self.group, other_args['at'].target, time * 60)
                    return MessageChain.create([Plain('禁言成功!')])
            elif subcommand.__contains__('unmute'):
                if subcommand['unmute'].__contains__('all'):
                    await self.app.unmuteAll(self.group.id)
                    return MessageChain.create([Plain('关闭全员禁言成功!')])
                elif isinstance(other_args['at'], At):
                    await self.app.unmuteMember(self.group, other_args['at'].target)
                    return MessageChain.create([Plain('解除禁言成功!')])
            elif subcommand.__contains__('func'):
                func = None
                if other_args.__contains__('card'):
                    func = 'member_card_change'
                elif other_args.__contains__('flash'):
                    func = 'flash_png'
                elif other_args.__contains__('kick'):
                    func = 'member_kick'
                elif other_args.__contains__('quit'):
                    func = 'member_quit'
                if func and await save_config(func, self.group.id, other_args['status']):
                    return MessageChain.create([Plain('开启成功！' if other_args['status'] else '关闭成功！')])
            elif subcommand.__contains__('刷屏检测'):
                if await save_config('mute', self.group.id, {
                    'time': other_args['time'],
                    'mute': other_args['mute_time'] * 60,
                    'message': other_args['reply']
                }):
                    return MessageChain.create([Plain('设置成功!')])
            elif subcommand.__contains__('重复消息'):
                if await save_config('duplicate', self.group.id, {
                    'time': other_args['time'],
                    'mute': other_args['mute_time'] * 60,
                    'message': other_args['reply']
                }):
                    return MessageChain.create([Plain('设置成功!')])
            elif subcommand.__contains__('超长消息'):
                if await save_config('over-length', self.group.id, {
                    'text': other_args['len'],
                    'mute': other_args['mute_time'] * 60,
                    'message': other_args['reply']
                }):
                    return MessageChain.create([Plain('设置成功!')])
            return self.args_error()
        except PermissionError:
            return self.exec_permission_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()
