import json
import random

from app.core.settings import GROUP_RUNING_LIST, config
from app.trigger.trigger import Trigger
from app.util.graia import At, Group, Plain, message
from app.util.network import general_request

no_answer = [
    "我好像忘了什么...",
    "你刚刚说什么？",
    "啊？",
    "我忘了你说的啥...",
    "我好像失忆了...",
    "等等，我想下要说什么!",
    "没理解你什么意思",
    "我听不懂你在说什么",
    "不听不听，王八念经！",
    "我有权保持沉默！",
    "No Answer!" "Pardon？",
    "Sorry, can you say that again?",
    "Could you repeat that please?",
    "Come again?",
    "I didn’t catch your meaning.",
    "I don’t get it.",
    "I didn’t follow you.",
    "I can’t hear you.",
    "Could you speak up a little bit?",
    "Could you slow down a little bit?",
]


class Chat(Trigger):
    """智能聊天系统"""

    async def process(self):
        if not isinstance(self.sender, Group) or not self.message.display or self.msg[0][0] in config.COMMAND_HEADERS:
            return
        msg = "".join(str(item).strip() for item in self.message.get(Plain) if str(item) is not None)
        if not msg:
            return
        url = "http://api.qingyunke.com/api.php"
        if (
            self.target.id in GROUP_RUNING_LIST
            or not self.message.has(At)
            or self.message.get_first(At).target != config.LOGIN_QQ
        ):
            return
        params = {
            "key": "free",
            "appid": 0,
            "msg": msg,
        }
        response = json.loads(await general_request(url=url, method="GET", params=params))
        resp = message(At(self.target))
        if response["result"] == 0:
            resp.extend(Plain(" " + str(response["content"]).replace("{br}", "\r\n").replace("菲菲", config.BOT_NAME)))
        else:
            resp.extend(Plain(f" {random.choice(no_answer)}"))
        resp.target(self.sender).send()
        self.as_last = True
