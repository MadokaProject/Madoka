from graia.application import MessageChain
from graia.application.message.elements.internal import Image

from app.api.tianyi import getHttp
from app.plugin.base import Plugin
from app.util.tools import isstartswith


class ACG(Plugin):
    entry = ['.acg']
    brief_help = '\r\n▶动漫图: acg'
    full_help = \
        '.acg 买家秀\r\n' \
        '.acg setu\r\n' \
        '.acg tui'

    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], '买家秀'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.sumt.cn/api/rand.tbimg.php")
                ])
            elif isstartswith(self.msg[0], 'setu'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.cyfan.top/acg")
                ])
            elif isstartswith(self.msg[0], 'tui'):
                url = 'http://tianyi.gjwa.cn/api/tu.php'
                response = await getHttp(url)
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress(response)
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
