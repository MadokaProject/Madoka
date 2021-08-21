from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image, At

from app.core.settings import *
from app.util.dao import MysqlDao
from app.util.tools import check_bot_permit


# crowd system manage 群管
async def csm(self, msg, type_record):
    if not check_bot_permit(self):
        if CONFIG.__contains__(str(self.group.id)) and CONFIG[str(self.group.id)].__contains__('status') and \
                CONFIG[str(self.group.id)]['status']:  # 默认关闭，需自行开启(.admin status)
            if await spam(self, msg, type_record):  # 刷屏检测(优先)
                return True


# 刷屏检测
async def spam(self, msg, type_record):
    try:
        with MysqlDao() as db:
            # 获取该群组某人的最后三条消息记录
            res = db.query('SELECT * FROM msg where uid=%s and qid=%s', [self.group.id, self.member.id])[-3:]
            if len(res) > 2:
                time = (res[2][3] - res[0][3]).seconds
                flood = CONFIG[str(self.group.id)]['mute'] if CONFIG[str(self.group.id)].__contains__('mute') else {
                    'time': 5, 'mute': 300, 'message': '请勿刷屏！'}
                duplicate = CONFIG[str(self.group.id)]['duplicate'] if CONFIG[str(self.group.id)].__contains__(
                    'duplicate') else {'time': 30, 'mute': 120, 'message': '请勿发送重复消息！'}
                if time < flood['time']:  # 刷屏禁言
                    await self.app.mute(self.group, self.member.id, flood['mute'])
                    resp = MessageChain.create([
                        At(self.member.id), Plain(' ' + flood['message'])
                    ])
                    await self._do_send(resp)
                    return True
                elif res[0][4] == res[1][4] == res[2][4] \
                        and res[0][4].strip() != '' and time < duplicate['time']:  # 30秒内重复消息禁言
                    await self.app.mute(self.group, self.member.id, duplicate['mute'])
                    resp = MessageChain.create([
                        At(self.member.id), Plain(' ' + duplicate['message'])
                    ])
                    await self._do_send(resp)
                    return True
        over_length = CONFIG[str(self.group.id)]['over-length'] if CONFIG[str(self.group.id)].__contains__(
            'over-length') else {'text': 500, 'image': 5, 'mute': 120, 'message': '请勿发送超长消息'}
        if (type_record == 'text' and len(msg) > over_length['text']) or (
                type_record == 'image' and len(self.message.get(Image)) > over_length['image']):
            await self.app.mute(self.group, self.member.id, over_length['mute'])
            resp = MessageChain.create([
                At(self.member.id), Plain(' ' + over_length['message'])
            ])
            await self._do_send(resp)
            return True
    except Exception as e:
        print(e)
