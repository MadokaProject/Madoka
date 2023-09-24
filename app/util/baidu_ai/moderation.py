from typing import Union

from aiohttp.client_exceptions import InvalidURL
from aip import AipContentCensor
from loguru import logger

from app.core.config import Config
from app.util.network import general_request
from app.util.tools import to_thread

if Config.baidu_ai.moderation.enable:
    client = AipContentCensor(
        Config.baidu_ai.moderation.app_id,
        Config.baidu_ai.moderation.api_key,
        Config.baidu_ai.moderation.secret_key,
    )


def text_moderation(text: str) -> dict[str, str]:
    """文本审核"""
    return client.textCensorUserDefined(text)


def image_moderation(image: bytes) -> dict[str, str]:
    """图像审核"""
    return client.imageCensorUserDefined(image)


async def text_moderation_async(text: str) -> dict:
    """文本审核"""
    if not Config.baidu_ai.moderation.enable:
        logger.warning("百度内容审核未启用")
        return {"status": False, "message": "百度内容审核未启用"}
    resp: dict[str, str] = await to_thread(text_moderation, text)
    if "error_code" in resp:
        return {"status": "error", "message": f"{resp['error_msg']} - {resp['error_code']}"}
    elif resp["conclusionType"] in (2, 3):
        return {"status": False, "message": ",\n".join(item["msg"] for item in resp["data"])}
    return {"status": True, "message": ",\n".join(item["msg"] for item in resp["data"]) if "data" in resp else None}


async def image_moderation_async(image: Union[str, bytes]) -> dict:
    """图像审核"""
    if not Config.baidu_ai.moderation.enable:
        logger.warning("百度内容审核未启用")
        return {"status": False, "message": "百度内容审核未启用"}
    if isinstance(image, str):
        try:
            image = await general_request(image, _type="bytes")
        except InvalidURL as e:
            return {"status": "error", "message": f"InvalidURL: {e}"}
    resp: dict[str, str] = await to_thread(image_moderation, image)
    if "error_code" in resp:
        return {"status": "error", "message": f"{resp['error_msg']} - {resp['error_code']}"}
    elif resp["conclusionType"] in (2, 3):
        return {"status": False, "message": ",\n".join(item["msg"] for item in resp["data"])}
    return {"status": True, "message": ",\n".join(item["msg"] for item in resp["data"]) if "data" in resp else None}
