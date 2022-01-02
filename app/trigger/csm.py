from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.model import MemberPerm
from loguru import logger

from app.core.settings import *
from app.trigger.trigger import Trigger
from app.util.control import Permission
from app.util.dao import MysqlDao


class CSM(Trigger):
    """群管系统"""

    async def process(self):
        if not hasattr(self, 'group') or self.check_admin(
                Permission.GROUP_ADMIN) or self.group.accountPerm == MemberPerm.Member:
            return
        if CONFIG.__contains__(str(self.group.id)) and CONFIG[str(self.group.id)].__contains__('status') and \
                CONFIG[str(self.group.id)]['status']:  # 默认关闭，需自行开启(.admin status)
            if await self.spam():  # 刷屏检测(优先)
                self.as_last = True

    # 刷屏检测
    async def spam(self):
        try:
            with MysqlDao() as db:
                # 获取该群组某人的最后三条消息记录
                res = db.query(
                    'SELECT * FROM msg where uid=%s and qid=%s ORDER BY id DESC LIMIT 3',
                    [self.group.id, self.member.id]
                )
                if len(res) > 2:
                    time = (res[0][3] - res[2][3]).seconds
                    flood = CONFIG[str(self.group.id)]['mute'] if CONFIG[str(self.group.id)].__contains__('mute') else {
                        'time': 5, 'mute': 300, 'message': '请勿刷屏！'}
                    duplicate = CONFIG[str(self.group.id)]['duplicate'] if CONFIG[str(self.group.id)].__contains__(
                        'duplicate') else {'time': 30, 'mute': 120, 'message': '请勿发送重复消息！'}
                    if time < flood['time']:  # 刷屏禁言
                        await self.app.muteMember(self.group, self.member.id, flood['mute'])
                        resp = MessageChain.create([
                            At(self.member.id), Plain(' ' + flood['message'])
                        ])
                        await self.do_send(resp)
                        return True
                    elif res[0][4] == res[1][4] == res[2][4] \
                            and res[0][4].strip() != '' and time < duplicate['time']:  # 30秒内重复消息禁言
                        await self.app.muteMember(self.group, self.member.id, duplicate['mute'])
                        resp = MessageChain.create([
                            At(self.member.id), Plain(' ' + duplicate['message'])
                        ])
                        await self.do_send(resp)
                        return True
            over_length = CONFIG[str(self.group.id)]['over-length'] if CONFIG[str(self.group.id)].__contains__(
                'over-length') else {'text': 500, 'mute': 120, 'message': '请勿发送超长消息'}
            if len(self.msg) > over_length['text']:
                await self.app.muteMember(self.group, self.member.id, over_length['mute'])
                resp = MessageChain.create([
                    At(self.member.id), Plain(' ' + over_length['message'])
                ])
                await self.do_send(resp)
                return True
        except Exception as e:
            logger.exception(e)
