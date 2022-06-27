import importlib

from loguru import logger

importlib.__import__("app.event.bot")
importlib.__import__("app.event.friend")
importlib.__import__("app.event.group")

logger.success("事件监听器启动成功")
