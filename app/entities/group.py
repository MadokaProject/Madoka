from peewee import IntegrityError

from app.plugin.basic.__06_permission.database.database import Group


class BotGroup:
    def __init__(self, group_id: int, active: int = 0):
        self.group_id = group_id
        self.active = active
        self.group_register()

    def group_register(self):
        """注册群组"""
        try:
            Group.create(uid=self.group_id, permission="*", active=self.active)
        except IntegrityError:
            if self.active:
                Group.update(active=self.active).where(Group.uid == self.group_id).execute()

    async def group_deactivate(self):
        """取消激活"""
        Group.update(active=0).where(Group.uid == self.group_id).execute()
