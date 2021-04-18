from graia.application import MessageChain
from graia.application.message.elements.internal import Plain

from app.core.settings import *
from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.decorator import permission_required
from app.util.tools import isstartswith


class GithubListener(Plugin):
    entry = ['.github']
    brief_help = '\r\n▶Github监听: github'
    full_help = \
        '.github add [repo_name] [repo_api]\t添加监听仓库\r\n' \
        '.github modify [repo_name] [name|api] [value]\t修改监听仓库配置\r\n' \
        '.github remove [repo_name]\t删除监听仓库\r\n' \
        '.github list\t列出所有监听仓库'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'add'):
                assert len(self.msg) == 3
                if self.msg[1] in REPO:
                    self.resp = MessageChain.create([
                        Plain('添加失败，该仓库名已存在！')
                    ])
                    return
                with MysqlDao() as db:
                    res = db.update(
                        'INSERT INTO github_config (repo, api) VALUES (%s, %s)',
                        [self.msg[1], self.msg[2]]
                    )
                    if not res:
                        raise Exception()
                    self.resp = MessageChain.create([
                        Plain("添加成功！")
                    ])
                    REPO.update({
                        self.msg[1]: self.msg[2]
                    })

            elif isstartswith(self.msg[0], 'modify'):
                assert len(self.msg) == 4
                if self.msg[1] not in REPO:
                    self.resp = MessageChain.create([
                        Plain('修改失败，该仓库名不存在！')
                    ])
                    return
                with MysqlDao() as db:
                    if self.msg[2] == 'name':
                        res = db.update(
                            'UPDATE github_config SET repo=%S WHERE repo=%s',
                            [self.msg[3], self.msg[1]]
                        )
                        REPO[self.msg[3]] = REPO.pop(self.msg[1])
                        if not res:
                            raise Exception()
                    elif self.msg[2] == 'api':
                        res = db.update(
                            'UPDATE github_config SET api=%s WHERE repo=%s',
                            [self.msg[3], self.msg[1]]
                        )
                        REPO[self.msg[1]] = self.msg[3]
                        if not res:
                            raise Exception()
                    else:
                        self.args_error()
                        return
                    if res:
                        self.resp = MessageChain.create([
                            Plain("修改成功！")
                        ])
            elif isstartswith(self.msg[0], 'remove'):
                assert len(self.msg) == 2
                if self.msg[1] not in REPO:
                    self.resp = MessageChain.create([
                        Plain('删除失败，该仓库名不存在！')
                    ])
                    return
                with MysqlDao() as db:
                    res = db.update(
                        'DELETE FROM github_config WHERE repo=%s',
                        [self.msg[1]]
                    )
                    if not res:
                        raise Exception
                    self.resp = MessageChain.create([
                        Plain("删除成功！")
                    ])
                    REPO.pop(self.msg[1])
            elif isstartswith(self.msg[0], 'list'):
                with MysqlDao() as db:
                    res = db.query(
                        "SELECT repo, api FROM github_config"
                    )
                self.resp = MessageChain.create([Plain(
                    '\r\n'.join([f'{repo}: {repo_api}' for (repo, repo_api) in res])
                )])
            else:
                self.args_error()
                return
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            print(e)
            self.unkown_error()
