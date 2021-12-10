from typing import Optional, Union
from graia.ariadne.context import ariadne_ctx
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.model import BotMessage, Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Source


async def safeSendGroupMessage(
    target: Union[Group, int],
    message: MessageChain,
    quote: Optional[Union[Source, int]] = None,
) -> BotMessage:
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
