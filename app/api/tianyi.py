import aiohttp
from retrying import retry

header = [
    {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 '
                   '(KHTML, like Gecko) Version/5.1 Safari/534.50'},
    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'}
]


@retry(stop_max_attempt_number=5, wait_fixed=5000)
async def getHttpGet(url, params):
    async with aiohttp.request("GET", url, params=params) as r:
        response = await r.text(encoding="utf-8")  # 或者直接await r.read()不编码，直接读取，适合于图像等无法编码文件
        return response


@retry(stop_max_attempt_number=5, wait_fixed=5000)
async def getHttp(url):
    async with aiohttp.request("GET", url) as r:
        response = await r.text(encoding='utf-8')
        return response


if __name__ == '__main__':
    url = 'http://tianyi.gjwa.cn/api/lingzan.php'
    param = {
        'qq': '3189402257'
    }
    response = getHttpGet(url, param)
