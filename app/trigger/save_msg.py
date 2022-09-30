from app.trigger.trigger import Trigger
from app.util.control import Permission
from app.util.graia import Group
from app.util.msg import save


class SaveMsg(Trigger):
    """消息存储"""

    async def process(self):
        if isinstance(self.sender, Group) or Permission.manual(self.target, Permission.MASTER):
            save(self.sender.id, self.target.id, self.message.as_persistent_string())
