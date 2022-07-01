from graia.ariadne.model import Group

from app.trigger.trigger import Trigger
from app.util.control import Permission
from app.util.msg import save


class SaveMsg(Trigger):
    """消息存储"""

    async def process(self):
        if not isinstance(self.sender, Group) or self.check_admin(Permission.MASTER):
            return
        if self.msg[0][0] in '.,;!?。，；！？/\\':
            return
        save(self.sender.id, self.target.id, self.message.display)
