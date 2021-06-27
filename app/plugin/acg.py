from graia.application import MessageChain
from graia.application.message.elements.internal import Image

from app.api.tianyi import getHttp
from app.plugin.base import Plugin
from app.util.tools import isstartswith


class ACG(Plugin):
    entry = ['.acg']
    brief_help = '\r\n▶动漫图: acg'
    full_help = \
        '.acg 0\r\n' \
        '.acg 1\r\n' \
        '.acg 2\r\n' \
        '.acg 3\r\n' \
        '.acg 4\r\n' \
        '.acg miku\r\n' \
        '.acg mjx\r\n' \
        '.acg tui\r\n' \
        '.acg tui1'

    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], '0'):
                Image.fromNetworkAddress("https://api.lyiqk.cn/api")
            elif isstartswith(self.msg[0], '1'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.ghser.com/random/api.php")
                ])
            elif isstartswith(self.msg[0], '2'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.cyfan.top/acg")
                ])
            elif isstartswith(self.msg[0], '3'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.ghser.com/random/pe.php")
                ])
            elif isstartswith(self.msg[0], '4'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.btstu.cn/sjbz/?lx=dongman")
                ])
            elif isstartswith(self.msg[0], 'miku'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.lyiqk.cn/miku")
                ])
            elif isstartswith(self.msg[0], 'mjx'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.lyiqk.cn/mjx")
                ])
            elif isstartswith(self.msg[0], 'tui'):
                url = 'http://api.kind8.cn/api/tu.php'
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress((await getHttp(url)).strip('\n'))
                ])
            elif isstartswith(self.msg[0], 'tui1'):
                url = 'http://api.ymong.top/api/meitui.php'
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress((await getHttp(url)).strip('\n'))
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
