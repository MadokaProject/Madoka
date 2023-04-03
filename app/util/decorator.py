import inspect
import threading
from typing import Callable


class Singleton(type):
    """单例模式"""

    _instances = {}
    lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            with self.lock:
                self._instances[self] = super().__call__(*args, **kwargs)
        return self._instances[self]

    @classmethod
    def remove(mcs, cls):
        mcs._instances.pop(cls, None)


class ArgsAssigner:
    """参数分配器"""

    def __init__(self, func: Callable):
        self.func = func
        self.signature = inspect.signature(self.func)

    def __call__(self, *args, **kwargs):
        self.args = []
        for i in self.signature.parameters.values():
            if str(i.kind) in {"POSITIONAL_OR_KEYWORD", "KEYWORD_ONLY"}:
                for arg in args:
                    _type = i.annotation
                    if hasattr(i.annotation, "__args__"):
                        _type = i.annotation.__args__
                    if isinstance(arg, _type):
                        self.args.append(arg)
                        break
                else:
                    if isinstance(i.default, type) and i.default.__name__ == "_empty":
                        self.args.append(None)
                    else:
                        self.args.append(i.default)
        return self.func(*self.args, **kwargs)
