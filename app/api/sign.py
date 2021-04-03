import random
import string
import time
from hashlib import md5
from urllib.parse import urlencode

import requests

"""
// getReqSign ：根据 接口请求参数 和 应用密钥 计算 请求签名
// 参数说明
//   - $params：接口请求参数（特别注意：不同的接口，参数对一般不一样，请以具体接口要求为准）
//   - $appkey：应用密钥
// 返回数据
//   - 签名结果
"""


# 对字典按键排序
def sort_by_key(d):
    """
    d.items() 返回元素为 (key, value) 的可迭代类型（Iterable），
    key 函数的参数 k 便是元素 (key, value)，所以 k[0] 取到字典的键。
    """
    return sorted(d.items(), key=lambda k: k[0])


# 生成随机字符串
def nonce_str():
    length = random.randint(1, 32)
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, length))
    return ran_str


def getReqSign(params, appkey):  # params: 关联数组 appkey: 字符串
    #  1. 字典升序排序
    params = dict(sort_by_key(params))

    # 2. 拼接URL键值对
    str = urlencode(params)

    #  3. 拼接app_key
    str += '&app_key=' + appkey

    #  4. MD5运算+转换大写，得到请求签名
    sign = md5(str.encode('utf8')).hexdigest().upper()
    return sign


def doHttpPost(param, url):
    params = {
        'app_id': '2169319723',
        'time_stamp': int(time.time()),
        'nonce_str': nonce_str(),
    }

    params.update(param)
    appkey = '4TQfIcw6oa8WoikE'
    params['sign'] = getReqSign(params, appkey)

    # 请求
    response = requests.post(url, data=params)
    if response.json()['ret'] == 0:
        return response.json()['data']
    else:
        return response.json()['msg']
