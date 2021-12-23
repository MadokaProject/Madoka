from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config, get_config
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.reply', '.回复']
    brief_help = '\r\n[√]\t群自定义回复: reply'
    full_help = \
        '.回复/.reply\t仅管理员可用\r\n' \
        '.回复/.reply 添加/add [keyword] [text]\t添加自定义回复\r\n' \
        '.回复/.reply 修改/modify [keyword] [text]\t修改自定义回复\r\n' \
        '.回复/.reply 删除/remove [keyword]\t删除自定义回复\r\n' \
        '.回复/.reply 列出/list\t列出自定义回复'

    @permission_required(level=Permission.GROUP_ADMIN)
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
            if isstartswith(self.msg[0], ['添加', 'add']):
                assert len(self.msg) == 3
                await save_config('group_reply', self.group.id, {self.msg[1]: self.msg[2]}, model='add')
                self.resp = MessageChain.create([Plain('添加/修改成功！')])
            elif isstartswith(self.msg[0], 'remove'):
                assert len(self.msg) == 2
                msg = '删除成功!' if await save_config('group_reply', self.group.id, self.msg[1],
                                                   model='remove') else '删除失败!该关键词不存在'
                self.resp = MessageChain.create([Plain(msg)])
            elif isstartswith(self.msg[0], 'list'):
                res = await get_config('group_reply', self.group.id)
                self.resp = MessageChain.create(
                    [Plain('\n'.join(f'{key}' for key in res.keys()) if res else '该群组暂未配置！')])
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
