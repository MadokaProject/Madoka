import random

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At

from app.api.doHttp import doHttpRequest
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
        if hasattr(self, 'friend') or not self.message.asDisplay() or self.msg[0][0] in '.,;!?。，；！？/\\':
            return
        config = Config()
        message = [str(item).strip() for item in self.message.get(Plain) if str(item) is not None]
        if not message or message[0] in '.,;!?。，；！？/\\':
            return
        message = ''.join(message)
        url = 'http://api.qingyunke.com/api.php'
        if hasattr(self, 'friend'):
            if self.friend.id in MEMBER_RUNING_LIST:
                return
        elif hasattr(self, 'group'):
            if self.group.id in GROUP_RUNING_LIST or not self.message.has(At) or self.message.getFirst(
                    At).target != int(config.LOGIN_QQ):
                return
        params = {
            'key': 'free',
            'appid': 0,
            'msg': message,
        }
        response = json.loads(await doHttpRequest(url=url, method='GET', params=params))
        resp = MessageChain.create([At(self.member.id) if hasattr(self, 'group') else None])
        if response['result'] == 0:
            resp.extend(MessageChain.create([
                Plain(str(response['content']).replace('{br}', '\r\n').replace('菲菲', config.BOT_NAME))
            ]))
        else:
            resp.extend(MessageChain.create([
                Plain(random.choice(no_answer))
            ]))
        await self.do_send(resp)
        self.as_last = True
