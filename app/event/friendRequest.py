from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

from app.core.config import Config
from app.core.settings import NEW_FRIEND


class FriendRequest:
    def __init__(self, app, event):
        self.app = app
        self.event = event

    async def process_event(self):
        config = Config()
        if config.ONLINE and config.DEBUG:
            return

        NEW_FRIEND.update({str(self.event.supplicant): self.event})
        await self.app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
            Plain('有人申请加我为好友'),
            Plain('\r\n昵称: ' + self.event.nickname),
            Plain('\r\nQQ: ' + str(self.event.supplicant)),
            Plain('\r\n来自群聊: ' + str(self.event.sourceGroup)),
            Plain('\r\n附加消息: ' + self.event.message),
            Plain('\r\n同意申请: .friend accept ' + str(self.event.supplicant)),
            Plain('\r\n拒绝申请: .friend reject ' + str(self.event.supplicant)),
            Plain('\r\n拒绝并不再接受: .friend areject' + str(self.event.supplicant))
        ]))
