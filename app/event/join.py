from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from graia.application.message.elements.internal import Plain, Image, At


class Join:
    def __init__(self, *args):
        """存储消息"""
        for arg in args:
            if isinstance(arg, Group):
                self.group = arg  # 加入群聊
            elif isinstance(arg, Member):
                self.member = arg  # 新加入成员
            elif isinstance(arg, GraiaMiraiApplication):
                self.app = arg  # 程序执行主体

    async def process_event(self):
        resp = MessageChain.create([
            At(self.member.id), Plain(' 欢迎您加入本群\r\n您可以畅快的与大家交流啦\r\n帮助菜单: \t.help'),
            Image.fromNetworkAddress('https://thirdqq.qlogo.cn/g?b=qq&nk=' + str(self.member.id) + '&s=4')
        ])
        await self.app.sendGroupMessage(self.group, resp)
