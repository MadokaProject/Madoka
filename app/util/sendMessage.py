from typing import Optional, Union

from graia.ariadne.context import ariadne_ctx
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Source
from graia.ariadne.model import BotMessage, Group, Friend


async def safeSendMessage(
        target: Union[Group, Friend, int],
        message: MessageChain,
        quote: Optional[Union[Source, int]] = None
) -> BotMessage:
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
        app = ariadne_ctx.get()
        if app.getGroup(target):
            return await safeSendGroupMessage(target, message, quote)
        elif app.getFriend(target):
            return await safeSendFriendMessage(target, message, quote)
        else:
            raise UnknownTarget


async def safeSendFriendMessage(
        target: Union[Friend, int],
        message: MessageChain,
        quote: Optional[Union[Source, int]] = None,
) -> BotMessage:
    """发送好友消息

    :param target: 指定好友
    :param message: 发送消息
    :param quote: 回复ID
    """
    app = ariadne_ctx.get()
    try:
        return await app.sendFriendMessage(target, message, quote=quote)
    except UnknownTarget:
        msg = []
        for element in message.__root__:
            msg.append(element)
        try:
            return await app.sendFriendMessage(
                target, MessageChain.create(msg), quote=quote
            )
        except UnknownTarget:
            return await app.sendFriendMessage(target, MessageChain(msg))


async def safeSendGroupMessage(
        target: Union[Group, int],
        message: MessageChain,
        quote: Optional[Union[Source, int]] = None,
) -> BotMessage:
    """发送群消息

    :param target: 指定群
    :param message: 发送消息
    :param quote: 回复ID
    """
    app = ariadne_ctx.get()
    try:
        return await app.sendGroupMessage(target, message, quote=quote)
    except UnknownTarget:
        msg = []
        for element in message.__root__:
            if isinstance(element, At):
                try:
                    member = await app.getMember(target, element.target)
                    name = member.name
                except Exception:
                    name = str(element.target)
                msg.append(Plain(name))
                continue
            msg.append(element)
        try:
            return await app.sendGroupMessage(
                target, MessageChain.create(msg), quote=quote
            )
        except UnknownTarget:
            return await app.sendGroupMessage(target, MessageChain.create(msg))
