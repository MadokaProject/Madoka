import aiohttp.client

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.api.doHttp import doHttpRequest


async def version_listener(app, config):
    remote_version_url = 'https://cdn.jsdelivr.net/gh/MadokaProject/Application@master/app/util/version.json'
    try:
        remote_info = await doHttpRequest(remote_version_url, method='get', _type='json')
        remote_version = remote_info['version']
        remote_update_logs = remote_info['update_log']
        if remote_version > config.INFO_VERSION:
            log_msg = ''
            for log in remote_update_logs:
                if log['version'] > config.INFO_VERSION:
                    log_msg += f"{log['version']}: {log['info']}\r\n"
                else:
                    break
            await app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
                Plain('检测到有新版本发布啦！\r\n'),
                Plain('更新提要：\r\n'),
                Plain(log_msg),
                Plain(f'详情内容请前往{config.INFO_REPO}查看')
            ]))
            await app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([Plain('发送.p u可进行更新操作')]))
    except aiohttp.client.ClientConnectorError:
        logger.warning('获取远程版本信息超时')
