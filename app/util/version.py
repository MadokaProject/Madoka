import aiohttp.client
from loguru import logger

from app.core.config import Config
from app.util.graia import Ariadne, MessageChain, Plain
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


async def check_version(app: Ariadne, config: Config):
    """检查版本信息"""
    try:
        remote_info = await general_request(config.REMOTE_VERSION_URL, method="get", _type="json")
        remote_version = remote_info["version"]
        remote_update_logs = remote_info["update_log"]
        logger.info(f"Remote Version: {remote_version}")
        if compare_version(remote_version, config.INFO_VERSION):
            log_msg = ""
            for log in remote_update_logs:
                if compare_version(log["version"], config.INFO_VERSION):
                    log_msg += f"{log['version']}: {log['info']}\r\n"
                else:
                    break
            await app.send_friend_message(
                config.MASTER_QQ,
                MessageChain(
                    [
                        Plain("检测到有新版本发布啦！\r\n"),
                        Plain("更新提要：\r\n"),
                        Plain(log_msg),
                        Plain(f"详情内容请前往{config.INFO_REPO}/releases查看"),
                    ]
                ),
            )
            await app.send_friend_message(config.MASTER_QQ, MessageChain([Plain("发送.p u可进行更新操作")]))
    except aiohttp.client.ClientConnectorError:
        logger.warning("获取远程版本信息超时")
    except Exception as e:
        logger.exception(f"获取远程版本信息失败{e}")


async def version_notice(app: Ariadne, config: Config):
    """版本信息"""
    logger.info(f"欢迎使用{config.INFO_NAME}")
    logger.info(f"Docs: {config.INFO_DOCS}")
    logger.info(f"Repo: {config.INFO_REPO}")
    logger.info(f"Remote Plugin Repo: {config.REMOTE_REPO_VERSION}")
    logger.info(f"Native Version: {config.INFO_VERSION}")
    await check_version(app, config)
