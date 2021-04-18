import base64
import random
import string

import requests
from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, Image

from app.api.sign import doHttpPost
from app.plugin.base import Plugin
from app.util.tools import isstartswith


class ImageRecognize(Plugin):
    entry = ['.st', '.识图']
    brief_help = '\r\n▶图片识别: st'
    full_help = \
        '.st sh [图片]\t看图说话\r\n' \
        '.st bq [图片]\t标签识别'

    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            image_base64 = jin(self.message.get(Image)[0].dict()['url'])['avatar']
            if isstartswith(self.msg[0], 'sh'):
                url = 'https://api.ai.qq.com/fcgi-bin/vision/vision_imgtotext'
                params = {
                    'image': image_base64,
                    'session_id': nonce_str()
                }
                response = doHttpPost(params, url)
                if response['ret'] == 0:
                    self.resp = MessageChain.create([
                        Plain('看图说话识别结果: ' + response['data']['text'])
                    ])
                else:
                    self.unkown_error()
            elif isstartswith(self.msg[0], 'bq'):
                url = 'https://api.ai.qq.com/fcgi-bin/image/image_tag'
                params = {
                    'image': image_base64
                }
                response = doHttpPost(params, url)
                if response['ret'] == 0:
                    self.resp = MessageChain.create([
                        Plain('图片标签识别结果: \r\n' + '\r\n'.join(
                            f'标签: {i["tag_name"]}\t置信度: {i["tag_confidence"]}' for i in response['data']['tag_list']))
                    ])
                else:
                    self.unkown_error()
            else:
                self.args_error()
                return
        except AssertionError as e:
            print(e)
            self.args_error()
        except Exception as e:
            print(e)
            self.unkown_error()


# 生成随机字符串
def nonce_str():
    length = random.randint(1, 64)
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, length))
    return ran_str


def jin(image_url):
    url = image_url
    res = requests.get(url=url)
    base64_data = base64.b64encode(res.content).decode()
    data = {
        'avatar': base64_data
    }
    return data
