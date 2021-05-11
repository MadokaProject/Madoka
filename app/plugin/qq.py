from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, At, Image

from app.api.tianyi import getHttpGet
from app.plugin.base import Plugin
from app.util.tools import isstartswith


class QQ(Plugin):
    entry = ['.qq']
    brief_help = '\r\n▶QQ: qq'
    full_help = \
        '.qq 名片赞\t领取名片赞\r\n' \
        '.qq 气泡 [id] [str]\tDIY聊天气泡\r\n' \
        '.qq 头像 [id(1: 女,2: 男,3: 情侣,4: 卡通)]\t随机获取QQ头像'

    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], '名片赞'):
                url = 'http://tianyi.gjwa.cn/api/lingzan.php'
                param = {
                    'qq': str(self.member.id)
                }
                response = (await getHttpGet(url, param)).split('\n')
                try:
                    if self.friend.id:
                        self.resp = MessageChain.create([
                            Plain('\n'.join(f'{response[i]}' for i in range(2, 6)))
                        ])
                except:
                    self.resp = MessageChain.create([
                        Plain('\n'.join(f'{response[i]}' for i in range(2, 6))), At(self.member.id)
                    ])
            elif isstartswith(self.msg[0], '气泡'):
                assert len(self.msg) == 3
                url = 'http://tianyi.gjwa.cn/api/diyble.php'
                param = {
                    'id': self.msg[1],
                    'msg': self.msg[2]
                }
                response = await getHttpGet(url, param)
                try:
                    if self.friend.id:
                        self.resp = MessageChain.create([
                            Plain(response)
                        ])
                except:
                    self.resp = MessageChain.create([
                        At(self.member.id), Plain(' ' + response)
                    ])
            elif isstartswith(self.msg[0], '头像'):
                assert len(self.msg) == 2
                url = 'http://tianyi.gjwa.cn/api/touxiang.php'
                param = {
                    'msg': self.msg[1]
                }
                response = (await getHttpGet(url, param)).split('\n')[2:-2]
                try:
                    if self.friend.id:
                        if self.msg[1] == '3':
                            self.resp = MessageChain.create([
                                Image.fromNetworkAddress(response[0][5:-1]),
                                Image.fromNetworkAddress(response[1][5:-1])
                            ])
                        else:
                            self.resp = MessageChain.create([
                                Image.fromNetworkAddress(response[0][5:-1])
                            ])
                except:
                    if self.msg[1] == '3':
                        self.resp = MessageChain.create([
                            At(self.member.id), Image.fromNetworkAddress(response[0][5:-1]),
                            Image.fromNetworkAddress(response[1][5:-1])
                        ])
                    else:
                        self.resp = MessageChain.create([
                            At(self.member.id), Image.fromNetworkAddress(response[0][5:-1])
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
