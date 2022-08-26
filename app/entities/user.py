from peewee import IntegrityError

from app.plugin.basic.__06_permission.database.database import User


class BotUser:
    def __init__(self, qq, point: int = 0, active: int = 0):
        self.qq = qq
        self.point = point
        self.active = active
        self.user_register()

    def user_register(self) -> None:
        """注册用户"""
        try:
            User.create(uid=self.qq, point=self.point, active=self.active)
        except IntegrityError:
            if self.active:
                User.update(active=self.active).where(User.uid == self.qq).execute()

    async def user_deactivate(self) -> None:
        """取消激活"""
        User.update(active=0).where(User.uid == self.qq).execute()

    @property
    async def level(self) -> int:
        """获取用户权限等级"""
        return User.get(User.uid == self.qq).level or -1

    async def grant_level(self, new_level: int) -> None:
        """修改用户权限

        :param new_level: 新权限等级
        """
        User.update(level=new_level).where(User.uid == self.qq).execute()
