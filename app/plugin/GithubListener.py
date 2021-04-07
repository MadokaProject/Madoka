from graia.application import MessageChain
from graia.application.message.elements.internal import Plain
from app.plugin.base import Plugin
from app.util.decorator import permission_required
from app.util.tools import isstartswith
from app.util.dao import MysqlDao


class GithubListener(Plugin):
    entry = ['.github']
    brief_help = '\r\n▶Github监听: github'
    full_help = \
        '.github add [repo_name] [repo_api]\t添加监听仓库\r\n' \
        '.github modify [repo_name] [name|api] [value]\t修改监听仓库配置\r\n' \
        '.github remove [repo_name]\t删除监听仓库'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'add'):
                assert len(self.msg) == 3
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT * FROM github_config WHERE repo=%s',
                        [self.msg[1]]
                    )
                    if not res:
                        res = db.update(
                            'INSERT INTO github_config (repo, api) VALUES (%s, %s)',
                            [self.msg[1], self.msg[2]]
                        )
                        if not res:
                            raise Exception()
                        self.resp = MessageChain.create([
                            Plain("添加成功！")
                        ])
                    else:
                        self.resp = MessageChain.create([
                            Plain("添加失败，该仓库名已存在！")
                        ])

            elif isstartswith(self.msg[0], 'modify'):
                assert len(self.msg) == 4
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT * FROM github_config WHERE repo=%s',
                        [self.msg[1]]
                    )
                    if res:
                        if self.msg[2] == 'name':
                            res = db.update(
                                'UPDATE github_config SET repo=%S WHERE repo=%s',
                                [self.msg[3], self.msg[1]]
                            )
                            if not res:
                                raise Exception()
                        elif self.msg[2] == 'api':
                            res = db.update(
                                'UPDATE github_config SET api=%s WHERE repo=%s',
                                [self.msg[3], self.msg[1]]
                            )
                            if not res:
                                raise Exception()
                        else:
                            self.args_error()
                            return
                        if res:
                            self.resp = MessageChain.create([
                                Plain("修改成功！")
                            ])
                    else:
                        self.resp = MessageChain.create([
                            Plain("修改失败，该仓库名不存在！")
                        ])
            elif isstartswith(self.msg[0], 'remove'):
                assert len(self.msg) == 2
                with MysqlDao() as db:
                    res = db.query(
                        'SELECT * FROM github_config WHERE repo=%s',
                        [self.msg[1]]
                    )
                    if res:
                        res = db.update(
                            'DELETE FROM github_config WHERE repo=%s',
                            [self.msg[1]]
                        )
                        if not res:
                            raise Exception
                        self.resp = MessageChain.create([
                            Plain("删除成功！")
                        ])
                    else:
                        self.resp = MessageChain.create([
                            Plain("删除失败，该仓库名不存在！")
                        ])
            else:
                self.args_error()
                return
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            print(e)
            self.unkown_error()
