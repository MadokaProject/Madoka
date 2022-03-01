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
    brief_help = '群自定义回复'
    full_help = {
        '仅管理员可用!': '',
        '添加, add': {
            '添加或修改自定义回复': '',
            '[keyword]': '触发关键词(存在时为修改回复内容)',
            '[text]': '回复内容'
        },
        '删除, remove': {
            '删除自定义回复': '',
            '[keyword]': '触发关键词'
        },
        '列出, list': '列出自定义回复'
    }

    @permission_required(level=Permission.GROUP_ADMIN)
    async def process(self):
        if not self.msg:
            await self.print_help()
            return
        try:
            if not hasattr(self, 'group'):
                self.resp = MessageChain.create([
                    Plain('请在群聊内使用该命令!')
                ])
                return
            if isstartswith(self.msg[0], ['添加', 'add']):
                assert len(self.msg) >= 3
                await save_config('group_reply', self.group.id, {self.msg[1]: self.msg[2:]}, model='add')
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
        except AssertionError:
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
