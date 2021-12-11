from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.plugin.base import Plugin
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config, get_config
from app.util.tools import isstartswith


class GroupJoin(Plugin):
    entry = ['.join', '.入群欢迎']
    brief_help = '\r\n[√]\t入群欢迎: join'
    full_help = \
        '.入群欢迎/.join\t仅管理可用\r\n' \
        '.入群欢迎/.join 设置/set [文本]\t设置入群欢迎消息\r\n' \
        '.入群欢迎/.join 查看/view\t查看入群欢迎消息\r\n' \
        '.入群欢迎/.join 开启/enable\t开启入群欢迎\r\n' \
        '.入群欢迎/.join 关闭/disable\t关闭入群欢迎'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if not hasattr(self, 'group'):
                self.resp = MessageChain.create([Plain('请在群组使用该命令！')])
                return
            if isstartswith(self.msg[0], ['设置', 'set']):
                assert len(self.msg) >= 2 and self.msg[1].isdigit()
                save_config('member_join', self.group.id, {
                    'active': 1,
                    'text': '\n'.join([f'{value}' for value in self.msg[1:]])
                })
                self.resp = MessageChain.create([Plain('设置成功！')])
            elif isstartswith(self.msg[0], ['查看', 'view']):
                res = get_config('member_join', self.group.id)
                if not res:
                    self.resp = MessageChain.create([Plain("该群组未配置欢迎消息！")])
                else:
                    self.resp = MessageChain.create([
                        Plain(f"欢迎消息：{res['text'] if res.__contains__('text') else '默认欢迎消息'}"),
                        Plain(f"\n开启状态：{res['active']}")
                    ])
            elif isstartswith(self.msg[0], ['开启', 'enable']):
                save_config('member_join', self.group.id, {'active': 1}, model='add')
                self.resp = MessageChain.create([Plain("开启成功！")])
            elif isstartswith(self.msg[0], ['关闭', 'disable']):
                save_config('member_join', self.group.id, {'active': 0}, model='add')
                self.resp = MessageChain.create([Plain("关闭成功！")])
            else:
                self.args_error()
                return
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
