import requests
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

from app.core.settings import *


async def TimingMessage(app):
    for i in ACTIVE_GROUP.keys():
        res = requests.get("https://api.cyfan.top/dujitang?nojs=true")
        await app.sendGroupMessage(i, MessageChain.create([
            Plain(res.text)
        ]))
