"""消息队列，控制消息发送频率"""
import asyncio
import time

from graia.ariadne.app import Ariadne
from loguru import logger

from app.util.decorator import Singleton
from app.util.link_list import ListCreate


class MQ(metaclass=Singleton):
    __app: Ariadne
    __launched: bool = False
    __message_queue: ListCreate = ListCreate()
    __limit: int

    def __init__(self, limit: int = 1.5):
        """初始化消息队列

        :param limit: 频率(秒)
        """
        self.__limit = limit

    @property
    def limit(self):
        return self.__limit

    def append(self, msg):
        self.__message_queue.push_back(msg)

    async def send(self, p):
        try:
            await p.data(self.__app)
        except Exception as e:
            logger.exception(e)
            logger.error("消息发送失败")

    async def __process(self):
        while True:
            await asyncio.sleep(self.limit)
            if not self.__message_queue.is_empty():
                p = self.__message_queue.head.next
                await self.send(p)
                p.delete()

    async def start(self, app):
        if not self.__launched:
            self.__app: Ariadne = app
            self.__launched = True
            logger.success("消息队列启动成功！")
            try:
                await self.__process()
            except Exception as e:
                logger.exception(e)
        else:
            logger.warning("消息队列已启动！")

    async def stop(self):
        logger.info("等待剩余消息发送完毕")
        for p in self.__message_queue:
            time.sleep(1.5)
            await self.send(p)
            p.delete()
        logger.success("消息队列已停止")


mq = MQ()
