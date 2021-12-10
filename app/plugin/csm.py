import asyncio

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from loguru import logger

from app.core.settings import *
from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.decorator import permission_required
from app.util.tools import isstartswith


class Admin(Plugin):
    entry = ['.csm', '.群管']
    brief_help = '\r\n[√]\t群管: csm'
    full_help = \
        '.群管/.csm\t仅限管理可用！\r\n' \
        '.群管/.csm 状态/status [0 / 1]\t群管开关\r\n' \
        '.群管/.csm 踢/kick [@qq]\t踢人\r\n' \
        '.群管/.csm 撤回/revoke [id]\t撤回消息\r\n' \
        '.群管/.csm 禁言/ban [time(m)] [@qq]\t禁言\r\n' \
        '.群管/.csm 全员禁言/aban\t全员禁言\r\n' \
        '.群管/.csm 解禁/unban [@qq]\t解除禁言\r\n' \
        '.群管/.csm 全员解禁/unaban\t解除全员禁言\r\n' \
        '.群管/.csm 刷屏检测 [时长(s)] [禁言时间(m)] [回复消息]\t检测[时长]内的3条消息\r\n' \
        '.群管/.csm 重复消息 [时长(s)] [禁言时间(m)] [回复消息]\t检测[时长]内的3条消息\r\n' \
        '.群管/.csm 超长消息 [文本长度] [禁言时间(m)] [回复消息]\t检测单消息是否超出[文本长度]'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
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
            elif isstartswith(self.msg[0], ['kick', '踢']):
                assert len(self.msg) == 2 and self.msg[1][1:].isdigit()
                await self.app.kickMember(self.group, int(self.msg[1][1:]))
                self.resp = MessageChain.create([
                    Plain('飞机票快递成功！')
                ])
            elif isstartswith(self.msg[0], ['ban', '禁言']):
                assert len(self.msg) == 3 and self.msg[1].isdigit()
                await self.app.muteMember(self.group, int(self.msg[2][1:]), int(self.msg[1]) * 60)
                self.resp = MessageChain.create([
                    Plain('禁言成功！')
                ])
            elif isstartswith(self.msg[0], ['unban', '解禁']):
                assert len(self.msg) == 2 and self.msg[1][1:].isdigit()
                await self.app.unmuteMember(self.group, int(self.msg[1][1:]))
                self.resp = MessageChain.create([
                    Plain('解除禁言成功！')
                ])
            elif isstartswith(self.msg[0], ['aban', '全员禁言']):
                await self.app.muteAll(self.group.id)
                self.resp = MessageChain.create([
                    Plain('全员禁言成功！')
                ])
            elif isstartswith(self.msg[0], ['unaban', '全员解禁']):
                await self.app.unmuteAll(self.group.id)
                self.resp = MessageChain.create([
                    Plain('全员解除禁言成功！')
                ])
            elif isstartswith(self.msg[0], ['status', '状态']):
                assert len(self.msg) == 2 and self.msg[1] in ['0', '1']
                with MysqlDao() as db:
                    if db.update(
                            'REPLACE INTO config(name, uid, value) VALUES(%s, %s, %s)',
                            ['status', self.group.id, self.msg[1]]
                    ):
                        if not CONFIG.__contains__(str(self.group.id)):
                            CONFIG.update({str(self.group.id): {}})
                        CONFIG[str(self.group.id)].update({
                            'status': self.msg[1]
                        })
                        self.resp = MessageChain.create([
                            Plain('开启成功！' if int(self.msg[1]) else '关闭成功！')
                        ])
            elif isstartswith(self.msg[0], '刷屏检测'):
                assert len(self.msg) == 4 and self.msg[1].isdigit() and self.msg[2].isdigit()
                with MysqlDao() as db:
                    if db.update(
                            'REPLACE INTO config(name, uid, value) VALUES(%s, %s, %s)',
                            ['mute', self.group.id, json.dumps({
                                'time': int(self.msg[1]),
                                'mute': int(self.msg[2]) * 60,
                                'message': self.msg[3]
                            })]
                    ):
                        if not CONFIG.__contains__(str(self.group.id)):
                            CONFIG.update({str(self.group.id): {}})
                        CONFIG[str(self.group.id)].update({
                            'mute': {
                                'time': int(self.msg[1]),
                                'mute': int(self.msg[2]) * 60,
                                'message': self.msg[3]
                            }
                        })
                        self.resp = MessageChain.create([
                            Plain('设置成功！')
                        ])
            elif isstartswith(self.msg[0], '重复消息'):
                assert len(self.msg) == 4 and self.msg[1].isdigit() and self.msg[2].isdigit()
                with MysqlDao() as db:
                    if db.update(
                            'REPLACE INTO config(name, uid, value) VALUES(%s, %s, %s)',
                            ['duplicate', self.group.id, json.dumps({
                                'time': int(self.msg[1]),
                                'mute': int(self.msg[2]) * 60,
                                'message': self.msg[3]
                            })]
                    ):
                        if not CONFIG.__contains__(str(self.group.id)):
                            CONFIG.update({str(self.group.id): {}})
                        CONFIG[str(self.group.id)].update({
                            'duplicate': {
                                'time': int(self.msg[1]),
                                'mute': int(self.msg[2]) * 60,
                                'message': self.msg[3]
                            }
                        })
                        self.resp = MessageChain.create([
                            Plain('设置成功！')
                        ])
            elif isstartswith(self.msg[0], '超长消息'):
                assert len(self.msg) == 5 and self.msg[1].isdigit() and self.msg[2].isdigit()
                with MysqlDao() as db:
                    if db.update(
                            'REPLACE INTO config(name, uid, value) VALUES(%s, %s, %s)',
                            ['over-length', self.group.id, json.dumps({
                                'text': int(self.msg[1]),
                                'mute': int(self.msg[3]) * 60,
                                'message': self.msg[4]
                            })]
                    ):
                        if not CONFIG.__contains__(str(self.group.id)):
                            CONFIG.update({str(self.group.id): {}})
                        CONFIG[str(self.group.id)].update({
                            'over-length': {
                                'text': int(self.msg[1]),
                                'mute': int(self.msg[3]) * 60,
                                'message': self.msg[4]
                            }
                        })
                        self.resp = MessageChain.create([
                            Plain('设置成功！')
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
            logger.exception(e)
            self.unkown_error()


if __name__ == '__main__':
    a = Admin(MessageChain.create([Plain(
        '.admin ban 123'
    )]))
    asyncio.run(a.get_resp())
    print(a.resp)
