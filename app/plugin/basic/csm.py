from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, At
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config


class Module(Plugin):
    entry = 'csm'
    brief_help = '群管'
    manager: CommandDelegateManager = CommandDelegateManager.get_instance()

    @permission_required(level=Permission.GROUP_ADMIN)
    @manager.register(
        Alconna(
            headers=manager.headers,
            command=entry,
            options=[
                Subcommand('mute', args=Args['at': At: ...], help_text='禁言指定群成员', options=[
                    Option('--time|-t', args=Args['time': int:10], help_text='禁言时间(分)'),
                    Option('--all|-a', help_text='开启全员禁言')
                ]),
                Subcommand('unmute', args=Args['at': At: ...], help_text='取消禁言指定群成员', options=[
                    Option('--all|-a', help_text='关闭全员禁言')
                ]),
                Subcommand('func', args=Args['status': bool], help_text='功能开关', options=[
                    Option('--card|-C', help_text='成员名片修改通知'),
                    Option('--flash|-F', help_text='闪照识别'),
                    Option('--recall|-R', help_text='撤回识别'),
                    Option('--kick|-K', help_text='成员被踢通知'),
                    Option('--quit|-Q', help_text='成员退群通知')
                ]),
                Option('status', args=Args['status': bool], help_text='开关群管'),
                Option('kick', args=Args['at': At], help_text='踢出指定群成员'),
                Option('revoke', args=Args['id': int], help_text='撤回消息, id=消息ID, 自最后一条消息起算'),
                Option('刷屏检测', args=Args['time': int, 'mute_time': int, 'reply': str],
                       help_text='检测time内的3条消息是否刷屏; time: 秒, mute_time: 分钟, reply: 回复消息'),
                Option('重复消息', args=Args['time': int, 'mute_time': int, 'reply': str],
                       help_text='检测time内的3条消息是否重复; time: 秒, mute_time: 分钟, reply: 回复消息'),
                Option('超长消息', args=Args['len': int, 'mute_time': int, 'reply': str],
                       help_text='检测单消息是否超出设定的长度; len: 文本长度, mute_time: 分钟, reply: 回复消息'),
            ],
            help_text='群管助手'
        )
    )
    async def process(self, command: Arpamar, alc: Alconna):
        components = command.options.copy()
        components.update(command.subcommands)
        if not components:
            return await self.print_help(alc.get_help())
        try:
            if not hasattr(self, 'group'):
                return MessageChain.create([Plain('请在群聊内使用该命令!')])
            if status := components.get('status'):
                if await save_config('status', self.group.id, status['status']):
                    return MessageChain.create([Plain('开启成功!' if status['status'] else '关闭成功!')])
            elif kick := components.get('kick'):
                await self.app.kickMember(self.group, kick['at'].target)
                return MessageChain.create([Plain('飞机票快递成功!')])
            elif revoke := components.get('revoke'):
                await self.app.recallMessage(self.message[Source][0].id - revoke['id'])
                return MessageChain.create([Plain('消息撤回成功!')])
            elif mute := components.get('mute'):
                if mute.get('all'):
                    await self.app.muteAll(self.group.id)
                    return MessageChain.create([Plain('开启全员禁言成功!')])
                elif target := mute.get('at'):
                    time = mute['time']['time'] if mute.get('time') else 10
                    await self.app.muteMember(self.group, target.target, time * 60)
                    return MessageChain.create([Plain('禁言成功!')])
            elif unmute := components.get('unmute'):
                if unmute.get('all'):
                    await self.app.unmuteAll(self.group.id)
                    return MessageChain.create([Plain('关闭全员禁言成功!')])
                elif target := unmute.get('at'):
                    await self.app.unmuteMember(self.group, target.target)
                    return MessageChain.create([Plain('解除禁言成功!')])
            elif func := components.get('func'):
                tag = None
                if func.get("card"):
                    tag = 'member_card_change'
                elif func.get("quit"):
                    tag = 'member_quit'
                elif func.get("kick"):
                    tag = 'member_kick'
                elif func.get("flash"):
                    tag = 'flash_png'
                elif func.get("recall"):
                    tag = 'member_recall'
                if tag and await save_config(tag, self.group.id, func['status']):
                    return MessageChain.create([Plain('开启成功！' if func['status'] else '关闭成功！')])
            elif repeat := components.get('刷屏检测'):
                if await save_config('mute', self.group.id, {
                    'time': repeat['time'],
                    'mute': repeat['mute_time'] * 60,
                    'message': repeat['reply']
                }):
                    return MessageChain.create([Plain('设置成功!')])
            elif duplicate := components.get('重复消息'):
                if await save_config('duplicate', self.group.id, {
                    'time': duplicate['time'],
                    'mute': duplicate['mute_time'] * 60,
                    'message': duplicate['reply']
                }):
                    return MessageChain.create([Plain('设置成功!')])
            elif too_long := components.get('超长消息'):
                if await save_config('over-length', self.group.id, {
                    'text': too_long['len'],
                    'mute': too_long['mute_time'] * 60,
                    'message': too_long['reply']
                }):
                    return MessageChain.create([Plain('设置成功!')])
            return self.args_error()
        except PermissionError:
            return self.exec_permission_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()
