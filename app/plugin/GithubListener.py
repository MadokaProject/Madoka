from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.core.settings import REPO
from app.plugin.base import Plugin
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.github']
    brief_help = '\r\n[√]\tGithub监听: github'
    full_help = \
        '.github\t仅管理可用\r\n' \
        '.github add [repo_name] [repo_api]\t添加监听仓库\r\n' \
        '.github modify [repo_name] [name|api] [value]\t修改监听仓库配置\r\n' \
        '.github remove [repo_name]\t删除监听仓库\r\n' \
        '.github list\t列出所有监听仓库'

    @permission_required(level=Permission.GROUP_ADMIN)
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'add'):
                assert len(self.msg) == 3
                group_id = str(self.group.id)
                if REPO.__contains__(group_id) and self.msg[1] in REPO[group_id]:
                    self.resp = MessageChain.create([Plain('添加失败，该仓库名已存在！')])
                    return
                if await save_config('repo', group_id, {self.msg[1]: self.msg[2]}, model='add'):
                    self.resp = MessageChain.create([Plain("添加成功！")])
                    if not REPO.__contains__(group_id):
                        REPO.update({group_id: {}})
                    REPO[group_id].update({self.msg[1]: self.msg[2]})
            elif isstartswith(self.msg[0], 'modify'):
                assert len(self.msg) == 4 and self.msg[2] in ['name', 'api']
                group_id = str(self.group.id)
                if not REPO.__contains__(group_id) or self.msg[1] not in REPO[group_id]:
                    self.resp = MessageChain.create([Plain('修改失败，该仓库名不存在！')])
                    return
                if self.msg[2] == 'name':
                    await save_config('repo', group_id, self.msg[1], model='remove')
                    await save_config('repo', group_id, {self.msg[3]: REPO[group_id][self.msg[1]]}, model='add')
                    REPO[group_id][self.msg[3]] = REPO[group_id].pop(self.msg[1])
                else:
                    await save_config('repo', group_id, {self.msg[1]: self.msg[3]}, model='add')
                    REPO[group_id][self.msg[1]] = self.msg[3]
                self.resp = MessageChain.create([Plain("修改成功！")])
            elif isstartswith(self.msg[0], 'remove'):
                assert len(self.msg) == 2
                group_id = str(self.group.id)
                if not REPO.__contains__(group_id) or self.msg[1] not in REPO[group_id]:
                    self.resp = MessageChain.create([Plain('删除失败，该仓库名不存在！')])
                    return
                await save_config('repo', group_id, self.msg[1], model='remove')
                REPO[group_id].pop(self.msg[1])
                self.resp = MessageChain.create([Plain("删除成功！")])
            elif isstartswith(self.msg[0], 'list'):
                self.resp = MessageChain.create([Plain(
                    '\r\n'.join([f'{name}: {api}' for name, api in REPO[str(self.group.id)].items()])
                )])
            else:
                self.args_error()
                return
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()
