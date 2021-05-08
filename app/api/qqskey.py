import requests
from retrying import retry


@retry(stop_max_attempt_number=5, wait_fixed=1000)
def getHttpPost():
    url = 'http://3g.gljlw.com/newsid/qrlogin.php?do=getqrpic'

    # 请求
    response = requests.post(url)
    if response.json()['saveOK'] == 0:
        return response.json()
    else:
        raise Exception


@retry(stop_max_attempt_number=5, wait_fixed=1000)
def doHttpPost(param):
    url = 'http://3g.gljlw.com/newsid/qrlogin.php?do=qqlogin&qrsig=' + param

    # 请求
    response = requests.post(url)
    return response.text


if __name__ == '__main__':
    get = getHttpPost()
    print(get)
    print(get['qrsig'])
    do = doHttpPost(get['qrsig'])[8:-3]
    print(do.split('","'))
