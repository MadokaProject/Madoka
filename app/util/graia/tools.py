from typing import Optional

from creart import it
from graia.ariadne.util.interrupt import FunctionWaiter
from graia.broadcast.interrupt import InterruptControl


class MadokaFunctionWaiter(FunctionWaiter):
    """去除 FunctionWaiter 的超时默认值"""

    async def wait(self, timeout: Optional[float] = None):
        """等待 Waiter

        Args:
            timeout (float, optional): 超时时间, 单位为秒
        """
        inc = it(InterruptControl)
        return await inc.wait(self, timeout=timeout)
