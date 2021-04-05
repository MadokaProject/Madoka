from graia.application import MessageChain
from graia.application.message.elements.internal import Plain

from app.api.sign import doHttpPost
from app.plugin.base import Plugin
from app.util.tools import isstartswith

form = {
    'en': [['zh', 'fr', 'es', 'it', 'de', 'tr', 'ru', 'pt', 'vi', 'id', 'ms', 'th'], '英译N'],
    'zh': [['en', 'fr', 'es', 'it', 'de', 'tr', 'ru', 'pt', 'vi', 'id', 'ms', 'th', 'jp', 'kr'], '中译N'],
    'fr': [['en', 'zh', 'es', 'it', 'de', 'tr', 'ru', 'pt'], '法译N'],
    'es': [['en', 'zh', 'fr', 'it', 'de', 'tr', 'ru', 'pt'], '西班牙译N'],
    'it': [['en', 'zh', 'fr', 'es', 'de', 'tr', 'ru', 'pt'], '意大利译N'],
    'de': [['en', 'zh', 'fr', 'es', 'it', 'tr', 'ru', 'pt'], '德译N'],
    'tr': [['en', 'zh', 'fr', 'es', 'it', 'de', 'ru', 'pt'], '土耳其译N'],
    'ru': [['en', 'zh', 'fr', 'es', 'it', 'de', 'tr', 'pt'], '俄文译N'],
    'pt': [['en', 'zh', 'fr', 'es', 'it', 'de', 'tr', 'ru'], '葡萄牙译N'],
    'vi': [['en', 'zh'], '越南译N'],
    'id': [['en', 'zh'], '印度尼西亚译N'],
    'ms': [['en', 'zh'], '马来西亚译N'],
    'th': [['en', 'zh'], '泰文译N'],
    'jp': [['zh'], '日译中'],
    'kr': [['zh'], '韩文译中']
}


class Translate(Plugin):
    entry = ['.fy', '.翻译']
    brief_help = '\r\n▶翻译: fy'
    full_help = '\r\n'.join(f'.fy {i} [' + ', '.join(form[i][0]) + '] [文本] \t' + form[i][1] for i in form.keys()) \
                + '\r\n.fy lc\t查看语言缩写'

    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'lc'):
                self.resp = MessageChain.create([Plain(
                    '缩写 --> 语言\r\n' + '\r\n'.join(f'{i} --> ' + form[i][1][:-2] + '文' for i in form.keys())
                )])
            elif self.msg[0] in form.keys() and self.msg[1] in form[self.msg[0]][0]:
                url = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_texttranslate'
                params = {
                    'text': ' '.join(f'{i}' for i in self.msg[2:]),
                    'source': self.msg[0],
                    'target': self.msg[1]
                }
                response = doHttpPost(params, url)
                if response['ret'] == 0:
                    self.resp = MessageChain.create([
                        Plain('"' + response['data']['source_text'] + '" 的翻译结果为：' + response['data']['target_text'])
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
