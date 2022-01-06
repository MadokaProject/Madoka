from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.api.doHttp import doHttpRequest
from app.core.config import Config


async def version_notice(app: Ariadne, config: Config):
    remote_version_url = 'https://cdn.jsdelivr.net/gh/MadokaProject/Application@feature/colsrch/version/app/util/version.json'
    logger.info(f'欢迎使用{config.INFO_NAME}')
    logger.info(f'Docs: {config.INFO_DOCS}')
    logger.info(f'Repo: {config.INFO_REPO}')
    logger.info(f'Version: {config.INFO_VERSION}')
    remote_info = await doHttpRequest(remote_version_url, method='get', _type='json')
    remote_version = remote_info['version']
    remote_update_logs = remote_info['update_log']
    logger.info(f'Remote version: {remote_version}')
    if remote_version > config.INFO_VERSION:
        log_msg = ''
        for log in remote_update_logs:
            if log['version'] > config.INFO_VERSION:
                log_msg += f"{log['version']}: {log['info']}\r\n"
            else:
                break
        await app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([
            Plain('当前不是最新版本，建议更新\r\n'),
            Plain('更新提要：\r\n'),
            Plain(log_msg),
            Plain(f'详情内容请前往{config.INFO_REPO}查看')
        ]))
        await app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([Plain('发送.p u可进行更新操作')]))
