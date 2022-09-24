from typing import Literal, Sequence, Union, overload

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import ActiveFriendMessage, ActiveGroupMessage
from graia.ariadne.message.chain import MessageChain, MessageContainer
from graia.ariadne.message.element import At, Element, Source
from graia.ariadne.model import Friend, Group, Member
from typing_extensions import Self

from app.core.app import AppCore
from app.extend.message_queue import mq

app: Ariadne = AppCore().get_app()


class Message:
    """对消息链的部分封装

    未封装的方法请通过content访问源消息链对象

    Typical usage example::
      >>> from app.util.graia import message
      >>> message([Plain("123456"), Image(url="https://example.com")])   # 创建消息链
      >>> .target(Group(1234567890))                                     # 指定消息发送对象
      >>> .at(Member(123456789))                                         # 指定@对象
      >>> .send()                                                        # 发送消息
    """

    __root__: MessageChain

    @property
    def content(self) -> MessageChain:
        """MessageChain"""
        return self.__root__

    @overload
    def __init__(self, __root__: Sequence[Element], *, inline: Literal[True]) -> None:
        ...

    @overload
    def __init__(self, *elements: MessageContainer, inline: Literal[False] = False) -> None:
        ...

    def __init__(
        self,
        __root__: MessageContainer,
        *elements: MessageContainer,
        inline: bool = False,
    ) -> None:
        """
        创建消息链.

        Args:
            *elements (Union[Iterable[Element], Element, str]): \
            元素的容器, 为承载元素的可迭代对象/单元素实例, \
            字符串会被自动不可逆的转换为 `Plain`

        Returns:
            MessageChain: 创建的消息链
        """
        self.__root__ = MessageChain(__root__, *elements, inline=inline)
        self.__target: Union[Friend, Member, Group, int] = None
        self.__quote: Union[Source, int] = None
        self.__at: list[Union[Member, int]] = []

    def send(self) -> None:
        """发送消息"""
        mq.put(self.__send)

    async def __send(self) -> Union[ActiveFriendMessage, ActiveGroupMessage]:
        """发送消息"""
        if not self.__target:
            raise ValueError("未指定消息发送对象")
        if isinstance(self.__target, int):
            self.__target = await app.get_friend(self.__target) or await app.get_group(self.__target)
            if not self.__target:
                raise ValueError("无法获取目标对象")
        if isinstance(self.__target, Friend):
            return await app.send_friend_message(self.__target, message=self.content, quote=self.__quote)
        elif isinstance(self.__target, Group):
            if self.__at:
                self.__root__ = MessageChain(At(at) for at in self.__at).extend(self.content)
                print(self.__root__)
            return await app.send_group_message(self.__target, message=self.content, quote=self.__quote)
        elif isinstance(self.__target, Member):
            return await app.send_temp_message(self.__target, message=self.content, quote=self.__quote)

    def target(self, target: Union[Friend, Member, Group, int]) -> Self:
        """指定消息发送对象

        Friend: -> 好友消息
        Group: -> 群组消息
        Member: -> 临时消息
        int: -> 自动查找好友对象 或 群组对象
        """
        assert isinstance(target, (Friend, Member, Group, int))
        self.__target = target
        return self

    def quote(self, quote: Union[Source, int]) -> Self:
        """指定回复消息元素"""
        assert isinstance(quote, (Source, int))
        self.quote = quote
        return self

    def at(self, at: Union[Member, int]) -> Self:
        """添加@对象

        只能在群组消息使用
        """
        assert isinstance(at, (Member, int))
        self.__at.append(at)
        return self

    def extend(self, *content: Union[Self, Element, list[Element, str]], copy: bool = False) -> Self:
        """扩展消息链"""
        self.__root__.extend(*content)
        return self
