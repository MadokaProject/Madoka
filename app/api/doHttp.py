import warnings

from app.util.doHttp import do_http_request as new_do_http_request


async def doHttpRequest(url, method='GET', _type='TEXT', params=None, headers=None, data=None):
    """通用Http异步请求函数

    :param url: str 请求的网址*
    :param method: str 请求方法
    :param _type: str 返回类型 [text(default),json,header, byte]
    :param params: dict param 请求参数
    :param headers: dict 请求头(可自动生成)
    :param data: body 请求参数
    :return: str
    """

    warnings.warn("该方法已被移至util目录，本文件将在下两个的版本移除，请修改导入路径为app.util.doHttp", DeprecationWarning)
    return new_do_http_request(url, method, _type, params, headers, data)
