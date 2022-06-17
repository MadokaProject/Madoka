from app.trigger.trigger import Trigger
from app.util.control import Permission
from app.util.msg import save


class SaveMsg(Trigger):
    """消息存储"""

    async def process(self):
        if not hasattr(self, 'group') or self.check_admin(Permission.MASTER) or self.msg[0][0] in '.,;!?。，；！？/\\':
            return
        save(self.group.id, self.member.id, self.message.display)
