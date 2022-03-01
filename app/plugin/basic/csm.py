from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from loguru import logger

from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.csm', '.群管']
    brief_help = '群管'
    full_help = {
        '仅限管理可用！': '',
        '状态, status': {
            '群管开关': '',
            '[0 / 1]': '开关可选值'
        },
        '踢, kick': {
            '踢人': '',
            '[@qq]': '@群成员'
        },
        '撤回, revoke': {
            '撤回消息': '',
            '[id]': '消息ID, 自最后一条消息起算'
        },
        '禁言, mute': {
            '禁言': '',
            '[time]': '禁言时间(分钟)',
            '[@qq]': '@群成员'
        },
        '全员禁言, allmute': '全员禁言',
        '解禁, unmute': {
            '解除禁言': '',
            '[@qq]': '@群成员'
        },
        '全员解禁, allunmute': '解除全员禁言',
        '名片通知, cardsend': {
            '成员名片修改通知': '',
            '[0 / 1]': '开关可选值'
        },
        '闪照识别, flashpng': {
            '闪照识别': '',
            '[0 / 1]': '开关可选值'
        },
        '被踢通知, kicksend': {
            '成员被踢通知': '',
            '[0 / 1]': '开关可选值'
        },
        '退群通知, quitsend': {
            '成员退群通知': '',
            '[0 / 1]': '开关可选值'
        },
        '刷屏检测': {
            '检测一定时间内的3条消息': '',
            '[时长]': '检测时长(秒)',
            '[禁言时间]': '禁言时长(分钟)',
            '[回复消息]': '触发后回复的消息'
        },
        '重复消息': {
            '检测一定时间内的3条消息': '',
            '[时长]': '检测时长(秒)',
            '[禁言时间]': '禁言时长(分钟)',
            '[回复消息]': '触发后回复的消息'
        },
        '超长消息': {
            '检测单消息是否超出设定的长度': '',
            '[文本长度]': '设定单消息允许的最大长度',
            '[禁言时间]': '禁言时长(分钟)',
            '[回复消息]': '触发后回复的消息'
        }
    }

    @permission_required(level=Permission.GROUP_ADMIN)
    async def process(self):
        if not self.msg:
            await self.print_help()
            return
        try:
            if not hasattr(self, 'group'):
                self.resp = MessageChain.create([
                    Plain('请在群聊内使用该命令!')
                ])
                return
            if isstartswith(self.msg[0], ['revoke', '撤回']):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                source = self.message[Source][0].id - int(self.msg[1])
                await self.app.recallMessage(source)
                self.resp = MessageChain.create([
                    Plain('消息撤回成功！')
                ])
            elif isstartswith(self.msg[0], ['kick', '踢'], full_match=1):
                assert len(self.msg) == 2 and self.msg[1][1:].isdigit()
                await self.app.kickMember(self.group, int(self.msg[1][1:]))
                self.resp = MessageChain.create([
                    Plain('飞机票快递成功！')
                ])
            elif isstartswith(self.msg[0], ['mute', '禁言'], full_match=1):
                assert len(self.msg) == 3 and self.msg[1].isdigit()
                await self.app.muteMember(self.group, int(self.msg[2][1:]), int(self.msg[1]) * 60)
                self.resp = MessageChain.create([
                    Plain('禁言成功！')
                ])
            elif isstartswith(self.msg[0], ['unmute', '解禁']):
                assert len(self.msg) == 2 and self.msg[1][1:].isdigit()
                await self.app.unmuteMember(self.group, int(self.msg[1][1:]))
                self.resp = MessageChain.create([
                    Plain('解除禁言成功！')
                ])
            elif isstartswith(self.msg[0], ['allmute', '全员禁言']):
                await self.app.muteAll(self.group.id)
                self.resp = MessageChain.create([
                    Plain('全员禁言成功！')
                ])
            elif isstartswith(self.msg[0], ['allunmute', '全员解禁']):
                await self.app.unmuteAll(self.group.id)
                self.resp = MessageChain.create([
                    Plain('全员解除禁言成功！')
                ])
            elif isstartswith(self.msg[0], ['status', '状态']):
                assert len(self.msg) == 2 and self.msg[1] in ['0', '1']
                if await save_config('status', self.group.id, int(self.msg[1])):
                    self.resp = MessageChain.create([Plain('开启成功！' if int(self.msg[1]) else '关闭成功！')])
            elif isstartswith(self.msg[0], '刷屏检测'):
                assert len(self.msg) == 4 and self.msg[1].isdigit() and self.msg[2].isdigit()
                if await save_config('mute', self.group.id, {
                    'time': int(self.msg[1]),
                    'mute': int(self.msg[2]) * 60,
                    'message': self.msg[3]
                }):
                    self.resp = MessageChain.create([Plain('设置成功！')])
            elif isstartswith(self.msg[0], '重复消息'):
                assert len(self.msg) == 4 and self.msg[1].isdigit() and self.msg[2].isdigit()
                if await save_config('duplicate', self.group.id, {
                    'time': int(self.msg[1]),
                    'mute': int(self.msg[2]) * 60,
                    'message': self.msg[3]
                }):
                    self.resp = MessageChain.create([Plain('设置成功！')])
            elif isstartswith(self.msg[0], '超长消息'):
                assert len(self.msg) == 4 and self.msg[1].isdigit() and self.msg[2].isdigit()
                if await save_config('over-length', self.group.id, {
                    'text': int(self.msg[1]),
                    'mute': int(self.msg[2]) * 60,
                    'message': self.msg[3]
                }):
                    self.resp = MessageChain.create([Plain('设置成功！')])
            elif isstartswith(self.msg[0], ['名片通知', 'cardsend'], full_match=1):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if await save_config('member_card_change', self.group.id, int(self.msg[1])):
                    self.resp = MessageChain.create([Plain('开启成功！' if int(self.msg[1]) else '关闭成功！')])
            elif isstartswith(self.msg[0], ['闪照识别', 'flashpng'], full_match=1):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if await save_config('flash_png', self.group.id, int(self.msg[1])):
                    self.resp = MessageChain.create([Plain('开启成功！' if int(self.msg[1]) else '关闭成功！')])
            elif isstartswith(self.msg[0], ['被踢通知', 'kicksend'], full_match=1):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if await save_config('member_kick', self.group.id, int(self.msg[1])):
                    self.resp = MessageChain.create([Plain('开启成功！' if int(self.msg[1]) else '关闭成功！')])
            elif isstartswith(self.msg[0], ['退群通知', 'quitsend'], full_match=1):
                assert len(self.msg) == 2 and self.msg[1].isdigit()
                if await save_config('member_quit', self.group.id, int(self.msg[1])):
                    self.resp = MessageChain.create([Plain('开启成功！' if int(self.msg[1]) else '关闭成功！')])
            else:
                self.args_error()
                return
        except PermissionError:
            self.exec_permission_error()
        except AssertionError:
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
