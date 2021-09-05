from app.trigger.trigger import Trigger
from app.util.msg import save


class SaveMsg(Trigger):
    """消息存储"""
    async def process(self):
        if not hasattr(self, 'group') or self.check_admin():
            return
        save(self.group.id, self.member.id, self.message.asDisplay())
