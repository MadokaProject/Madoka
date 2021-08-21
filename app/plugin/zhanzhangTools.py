import ast

from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, At

from app.api.tianyi import getHttpGet
from app.plugin.base import Plugin
from app.util.tools import isstartswith


class WebMasterTools(Plugin):
    entry = ['.web', '.站长', '.zhanzhang']
    brief_help = '\r\n▶站长工具: web'
    full_help = \
        '.web ping [域名]\r\n' \
        '.web 网站测速 [域名]\r\n' \
        '.web 域名查询 [域名]\r\n' \
        '.web 状态查询 [域名]\r\n' \
        '.web 百度收录 [域名]'
    enable = False

    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'ping'):
                url = 'http://tianyi.gjwa.cn/api/ping.php'
                param = {
                    'url': self.msg[1]
                }
                response = (await getHttpGet(url, param)).split('\n')
                try:
                    if self.friend.id:
                        self.resp = MessageChain.create([
                            Plain('\n'.join(f' {i}' for i in response))
                        ])
                except:
                    self.resp = MessageChain.create([
                        At(self.member.id), Plain('\n'.join(f' {i}' for i in response))
                    ])
            elif isstartswith(self.msg[0], '网站测速'):
                url = 'http://tianyi.gjwa.cn/api/cs.php'
                param = {
                    'url': self.msg[1]
                }
                response = (await getHttpGet(url, param)).split('\n')
                try:
                    if self.friend.id:
                        self.resp = MessageChain.create([
                            Plain('\n'.join(f' {i}' for i in response))
                        ])
                except:
                    self.resp = MessageChain.create([
                        At(self.member.id), Plain('\n'.join(f' {i}' for i in response))
                    ])
            elif isstartswith(self.msg[0], '域名查询'):
                url = 'http://tianyi.gjwa.cn/api/ymxx.php'
                param = {
                    'url': self.msg[1]
                }
                response = (await getHttpGet(url, param)).split('\n')
                try:
                    if self.friend.id:
                        self.resp = MessageChain.create([
                            Plain('\n'.join(f' {i}' for i in response))
                        ])
                except:
                    self.resp = MessageChain.create([
                        At(self.member.id), Plain('\n'.join(f' {i}' for i in response))
                    ])
            elif isstartswith(self.msg[0], '状态查询'):
                url = 'http://tianyi.gjwa.cn/api/status.php'
                param = {
                    'url': self.msg[1]
                }
                response = (await getHttpGet(url, param)).split('\n')
                try:
                    if self.friend.id:
                        self.resp = MessageChain.create([
                            Plain('\n'.join(f' {i}' for i in response))
                        ])
                except:
                    self.resp = MessageChain.create([
                        At(self.member.id), Plain('\n'.join(f' {i}' for i in response))
                    ])
            elif isstartswith(self.msg[0], '百度收录'):
                url = 'http://tianyi.gjwa.cn/api/shouqu.php'
                param = {
                    'domain': self.msg[1]
                }
                response = ast.literal_eval(await getHttpGet(url, param))
                self.resp = MessageChain.create([
                    Plain('域名：' + response['domain'] + '\n百度收录量：' + response['data'])
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
