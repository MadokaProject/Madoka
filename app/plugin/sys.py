from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.appCore import AppCore
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.sys', '.系统']
    brief_help = '\r\n[√]\t系统: sys'
    full_help = \
        '.系统/.sys\t仅限主人可用！\r\n' \
        '.系统/.sys 禁言退群 [0/ 1]\t设置机器人被禁言是否退群\r\n' \
        '.系统/.sys 重载插件/reload\t重新加载插件'
    hidden = True

    @permission_required(level=Permission.MASTER)
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if not hasattr(self, 'group'):
                self.resp = MessageChain.create([
                    Plain('请在群聊内使用该命令!')
                ])
                return
            if isstartswith(self.msg[0], '禁言退群'):
                assert len(self.msg) == 2 and self.msg[1] in ['0', '1']
                if await save_config('bot_mute_event', self.group.id, int(self.msg[1])):
                    self.resp = MessageChain.create([Plain('开启成功！' if int(self.msg[1]) else '关闭成功！')])
            elif isstartswith(self.msg[0], ['重载插件', 'reload']):
                core: AppCore = AppCore.get_core_instance()
                core.load_plugin_modules()
                self.resp = MessageChain.create([Plain('重载成功！')])
            else:
                self.args_error()
                return
        except PermissionError as e:
            print(e)
            self.exec_permission_error()
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
