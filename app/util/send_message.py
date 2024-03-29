from typing import Optional, Union

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import ActiveMessage
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Source
from graia.ariadne.model import Friend, Group
from loguru import logger

from app.core.app import AppCore

app: Ariadne = AppCore().get_app()


async def safeSendMessage(
    target: Union[Group, Friend, int],
    message: MessageChain,
    quote: Optional[Union[Source, int]] = None,
) -> Optional[ActiveMessage]:
    """发送消息

    :param target: 指定群组或好友
    :param message: 发送消息
    :param quote: 回复ID
    """
    if isinstance(target, Group):
        return await safeSendGroupMessage(target, message, quote)
    elif isinstance(target, Friend):
        return await safeSendFriendMessage(target, message, quote)
    else:
        if app.get_group(target):
            return await safeSendGroupMessage(target, message, quote)
        elif app.get_friend(target):
            return await safeSendFriendMessage(target, message, quote)
        else:
            logger.warning("发送消息失败")


async def safeSendFriendMessage(
    target: Union[Friend, int],
    message: MessageChain,
    quote: Optional[Union[Source, int]] = None,
) -> Optional[ActiveMessage]:
    """发送好友消息

    :param target: 指定好友
    :param message: 发送消息
    :param quote: 回复ID
    """
    try:
        return await app.send_friend_message(target, message, quote=quote)
    except UnknownTarget:
        msg = list(message.__root__)
        try:
            return await app.send_friend_message(target, MessageChain(msg), quote=quote)
        except UnknownTarget:
            try:
                return await app.send_friend_message(target, MessageChain(msg))
            except UnknownTarget:
                logger.warning("发送好友消息失败")


async def safeSendGroupMessage(
    target: Union[Group, int],
    message: MessageChain,
    quote: Optional[Union[Source, int]] = None,
) -> Optional[ActiveMessage]:
    """发送群消息

    :param target: 指定群
    :param message: 发送消息
    :param quote: 回复ID
    """
    try:
        return await app.send_group_message(target, message, quote=quote)
    except UnknownTarget:
        msg = []
        for element in message.__root__:
            if isinstance(element, At):
                try:
                    member = await app.get_member(target, element.target)
                    name = member.name
                except Exception:
                    name = str(element.target)
                msg.append(Plain(name))
                continue
            msg.append(element)
        try:
            return await app.send_group_message(target, MessageChain(msg), quote=quote)
        except UnknownTarget:
            try:
                return await app.send_group_message(target, MessageChain(msg))
            except UnknownTarget:
                logger.warning("发送群消息失败")
