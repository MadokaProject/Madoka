import re

from app.core.config import Config
from app.trigger.trigger import Trigger
from app.util.graia import At, Group, MessageChain, Plain
from app.util.online_config import get_config


class GroupQA(Trigger):
    """群问答"""

    async def process(self):
        if not isinstance(self.sender, Group) or self.msg[0][0] in Config.command.headers:
            return
        if res := await self.matcher():
            await self.do_send(MessageChain([At(self.target), Plain(f" {res}")]))
            self.as_last = True

    async def matcher(self):
        res: list[dict[str, str]] = await get_config("group_qa", self.sender.id)
        message = self.message.display
        for item in res:
            if item["pattern"] == "head" and self.head_matcher(message, item["keyword"]):
                return item["message"]
            elif item["pattern"] == "tail" and self.tail_matcher(message, item["keyword"]):
                return item["message"]
            elif item["pattern"] == "full" and self.full_matcher(message, item["keyword"]):
                return item["message"]
            elif item["pattern"] in ("arbitrary", "regex") and self.regex_matcher(message, item["keyword"]):
                return item["message"]
        return False

    @staticmethod
    def head_matcher(context: str, keyword):
        """头匹配"""
        return context.startswith(keyword)

    @staticmethod
    def tail_matcher(context: str, keyword):
        """尾匹配"""
        return context.endswith(keyword)

    @staticmethod
    def full_matcher(context: str, keyword):
        """完全匹配"""
        return context == keyword

    @staticmethod
    def regex_matcher(context: str, keyword):
        """正则匹配"""
        return bool(re.search(keyword, context))
