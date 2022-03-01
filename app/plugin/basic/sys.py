from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.sys', '.系统']
    brief_help = '系统'
    full_help = {
        '仅限主人可用!': '',
        '禁言退群': {
            '设置机器人禁言是否退群': '',
            '[0 / 1]': '开关'
        },
        '上线通知': {
            '设置机器人上线是否通知该群': '',
            '[0 / 1]': '开关'
        }
    }
    hidden = True

    @permission_required(level=Permission.MASTER)
    async def process(self):
        if not self.msg:
            await self.print_help()
            return
        try:
            if isstartswith(self.msg[0], ['禁言退群', '上线通知']):
                if not hasattr(self, 'group'):
                    self.resp = MessageChain.create([Plain('请在群聊内使用该命令!')])
                    return
                assert len(self.msg) == 2 and self.msg[1] in ['0', '1']
                config_name = {'禁言退群': 'bot_mute_event', '上线通知': 'online_notice'}[self.msg[0]]
                if await save_config(config_name, self.group.id, int(self.msg[1])):
                    self.resp = MessageChain.create([Plain('开启成功！' if int(self.msg[1]) else '关闭成功！')])
            else:
                self.args_error()
                return
        except AssertionError:
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
