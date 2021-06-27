from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image, At

from app.util.brushscreen import brushscreen
from app.util.msg import save


async def MsgProcess(self, msg):
    try:
        content_record = self.message.get(Plain)[0].dict()['text']
        type_record = 'text'
    except:
        content_record = self.message.get(Image)[0].dict()['url']
        type_record = 'image'
    content_record = msg if type_record == 'text' else content_record
    save(self.group.id, self.member.id, content_record)

    # 检测是否刷屏
    try:
        target_brushscreen = brushscreen(self.group.id, self.member.id)
        if target_brushscreen == 1:
            await self.app.mute(self.group, self.member.id, 5 * 60)
            resp = MessageChain.create([
                At(self.member.id), Plain(' 请勿刷屏！')
            ])
            await self._do_send(resp)
            return
        elif target_brushscreen == 2:
            await self.app.mute(self.group, self.member.id, 2 * 60)
            resp = MessageChain.create([
                At(self.member.id), Plain(' 请勿发送重复消息！')
            ])
            await self._do_send(resp)
            return
        elif (type_record == 'text' and len(msg) > 500) or (
                type_record == 'image' and len(self.message.get(Image)) > 5):
            await self.app.mute(self.group, self.member.id, 2 * 60)
            resp = MessageChain.create([
                At(self.member.id), Plain(' 请勿发送超长消息！')
            ])
            await self._do_send(resp)
            return
    except Exception as e:
        print(e)
