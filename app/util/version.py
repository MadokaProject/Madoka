import aiohttp.client
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.api.doHttp import doHttpRequest
from app.core.config import Config


def compare_version(native_version: str, remote_version: str):
    """比较版本号"""
    native_version = native_version.split('-')
    remote_version = remote_version.split('-')
    if len(remote_version) == 1:
        if remote_version[0] > native_version[0]:
            return True
        elif remote_version[0] == native_version[0] and len(native_version) == 2:
            return True
    else:
        if remote_version[0] > native_version[0]:
            return True
        if remote_version[0] == native_version[0] and remote_version[1] > native_version[1]:
            return True
    return False


async def check_version(app: Ariadne, config: Config):
    """检查版本信息"""
    try:
        remote_version_url = 'https://cdn.jsdelivr.net/gh/MadokaProject/Application@master/app/util/version.json'
        remote_info = await doHttpRequest(remote_version_url, method='get', _type='json')
        remote_version = remote_info['version']
        remote_update_logs = remote_info['update_log']
        logger.info(f'Remote version: {remote_version}')
        if compare_version(remote_version, config.INFO_VERSION):
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
                Plain(f'详情内容请前往{config.INFO_REPO}/releases查看')
            ]))
            await app.sendFriendMessage(config.MASTER_QQ, MessageChain.create([Plain('发送.p u可进行更新操作')]))
    except aiohttp.client.ClientConnectorError:
        logger.warning('获取远程版本信息超时')
    except Exception as e:
        logger.exception(f'获取远程版本信息失败{e}')


async def version_notice(app: Ariadne, config: Config):
    """版本信息"""
    logger.info(f'欢迎使用{config.INFO_NAME}')
    logger.info(f'Docs: {config.INFO_DOCS}')
    logger.info(f'Repo: {config.INFO_REPO}')
    logger.info(f'Native version: {config.INFO_VERSION}')
    await check_version(app, config)
