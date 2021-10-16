import random

from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, At

from app.api.doHttp import doHttpRequest
from app.core.config import *
from app.core.settings import *
from app.trigger.trigger import Trigger

no_answer = [
    '我好像忘了什么...',
    '你刚刚说什么？',
    '啊？',
    '我忘了你说的啥...',
    '我好像失忆了...',
    '等等，我想下要说什么!',
    '没理解你什么意思',
    '我听不懂你在说什么',
    '不听不听，王八念经！',
    '我有权保持沉默！',
    'No Answer!'
    'Pardon？',
    'Sorry, can you say that again?',
    'Could you repeat that please?',
    'Come again?',
    'I didn’t catch your meaning.',
    'I don’t get it.',
    'I didn’t follow you.',
    'I can’t hear you.',
    'Could you speak up a little bit?',
    'Could you slow down a little bit?'
]


class Chat(Trigger):
    """智能聊天系统"""
    async def process(self):
        head, sep, message = self.message.asDisplay().partition(' ')
        url = 'http://api.qingyunke.com/api.php'
        if hasattr(self, 'friend'):  # 好友聊天
            if not head or head[0] in '.,;!?。，；！？/\\':
                return
            params = {
                'key': 'free',
                'appid': 0,
                'msg': head,
            }
            response = json.loads(await doHttpRequest(url, 'GET', params))
            if response['result'] == 0:
                resp = MessageChain.create([
                    Plain(str(response['content']).replace('{br}', '\r\n').replace('菲菲', BOTNAME))
                ])
            else:
                resp = MessageChain.create([
                    Plain(random.choice(no_answer))
                ])
            await self.do_send(resp)
            self.as_last = True
        elif hasattr(self, 'group'):
            if not message or message[0] in '.,;!?。，；！？/\\':
                return
            if self.message.get(At) and str(self.message.get(At)[0].dict()['target']) == QQ:  # 群聊聊天
                params = {
                    'key': 'free',
                    'appid': 0,
                    'msg': message,
                }
                response = json.loads(await doHttpRequest(url, 'GET', params))
                if response['result'] == 0:
                    resp = MessageChain.create([
                        At(self.member.id), Plain(' ' + str(response['content']).replace('{br}', '\r\n').replace('菲菲', BOTNAME))
                    ])
                else:
                    resp = MessageChain.create([
                        At(self.member.id), Plain(' ' + random.choice(no_answer))
                    ])
                await self.do_send(resp)
                self.as_last = True
