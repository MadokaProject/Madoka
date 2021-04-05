from graia.application import MessageChain
from graia.application.message.elements.internal import Image

from app.plugin.base import Plugin
from app.util.tools import isstartswith


class ACG(Plugin):
    entry = ['.acg']
    brief_help = '\r\n▶动漫图: acg'
    full_help = \
        '.acg 买家秀\r\n' \
        '.acg setu'

    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], '买家秀'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.66mz8.com/api/rand.tbimg.php?format=jpg").asFlash()
                ])
            elif isstartswith(self.msg[0], 'setu'):
                self.resp = MessageChain.create([
                    Image.fromNetworkAddress("https://api.cyfan.top/acg")
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
