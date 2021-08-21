import random

from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, At

from app.api.sign import doHttpPost
from app.core.config import *
from app.core.settings import *

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


async def Chat(self):
    try:
        message = str(self.message.get(Plain)[0].dict()['text']).strip()
        url = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat'
        try:
            if self.friend.id:  # 好友聊天
                if message:
                    params = {
                        'session': str(self.friend.id),
                        'question': message.encode('utf-8'),
                    }
                    response = doHttpPost(params, url)
                    if response['ret'] == 0:
                        resp = MessageChain.create([
                            Plain(' ' + response['data']['answer'])
                        ])
                    else:
                        resp = MessageChain.create([
                            Plain(random.choice(no_answer))
                        ])
                    await self._do_send(resp)
        except:
            if self.message.get(At):  # 群聊聊天
                if str(self.message.get(At)[0].dict()['target']) == QQ:
                    if message:
                        params = {
                            'session': str(self.member.id),
                            'question': message.encode('utf-8'),
                        }
                        response = doHttpPost(params, url)
                        if response['ret'] == 0:
                            resp = MessageChain.create([
                                At(self.member.id), Plain(' ' + response['data']['answer'])
                            ])
                        else:
                            resp = MessageChain.create([
                                At(self.member.id), Plain(' ' + random.choice(no_answer))
                            ])
                        await self._do_send(resp)
                    else:
                        if self.member.id == ADMIN_USER:
                            resp = MessageChain.create([
                                At(self.member.id), Plain(' 管理员您好')
                            ])
                        else:
                            resp = MessageChain.create([
                                At(self.member.id), Plain(' 爪巴')
                            ])
                        await self._do_send(resp)
    except Exception as e:
        print(e)
