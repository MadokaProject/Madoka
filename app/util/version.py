import json

import aiohttp.client
from loguru import logger

from app.core.config import Config, MadokaInfo
from app.util.graia import Plain, message
from app.util.network import general_request


def compare_version(remote_version: str, native_version: str) -> bool:
    """比较版本号

    :param remote_version: 远程版本号
    :param native_version: 本地版本号
    """
    native_version = native_version.split("-")
    remote_version = remote_version.split("-")
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


async def check_version():
    """检查版本信息"""
    try:
        remote_info = json.loads(await general_request(MadokaInfo.REMOTE_VERSION_URL, method="get", _type="text"))
        remote_version = remote_info["version"]
        remote_update_logs = remote_info["update_log"]
        logger.info(f"Remote Version: {remote_version}")
        if compare_version(remote_version, MadokaInfo.VERSION):
            log_msg = ""
            for log in remote_update_logs:
                if compare_version(log["version"], MadokaInfo.VERSION):
                    log_msg += f"{log['version']}: {log['info']}\r\n"
                else:
                    break
            message(
                [
                    Plain("检测到有新版本发布啦！\r\n"),
                    Plain("更新提要：\r\n"),
                    Plain(log_msg),
                    Plain(f"详情内容请前往{MadokaInfo.REPO}/releases查看"),
                ]
            ).target(Config.master_qq).send()
            message("发送.p u可进行更新操作").target(Config.master_qq).send()
    except aiohttp.client.ClientConnectorError:
        logger.warning("获取远程版本信息超时")
    except Exception as e:
        logger.exception(f"获取远程版本信息失败{e}")


async def version_notice():
    """版本信息"""
    logger.info(f"欢迎使用{MadokaInfo.NAME}")
    logger.info(f"Docs: {MadokaInfo.DOCS}")
    logger.info(f"Repo: {MadokaInfo.REPO}")
    logger.info(f"Remote Plugin Repo: {MadokaInfo.REMOTE_REPO_VERSION}")
    logger.info(f"Native Version: {MadokaInfo.VERSION}")
    await check_version()
