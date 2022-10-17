from . import Error


class CommandManagerInitializedError(Error):
    """命令管理器未初始化"""

    def __init__(self):
        Error.__init__(self, "CommandManager is not initialized")


class CommandManagerAlreadyInitializedError(Error):
    """命令管理器重复初始化"""

    def __init__(self):
        Error.__init__(self, "CommandManager is already initialized")


class FrequencyLimitError(Error):
    """频率限制"""

    pass


class FrequencyLimitExceededError(FrequencyLimitError):
    """群组请求超出负载权重限制"""

    def __init__(self, target, time: float):
        Error.__init__(self, "Frequency limit exceeded: %r, Remaining disable time: %.2f" % (target, time))
        self.target = target
        self.time = time
        self.args = (target, time)


class FrequencyLimitExceededDoNothingError(FrequencyLimitError):
    """请求者在黑名单中不作回应"""

    def __init__(self, target, time: float):
        Error.__init__(
            self, "Frequency limit exceeded and do nothing: %r, Remaining disable time: %.2f" % (target, time)
        )
        self.target = target
        self.limit = time
        self.args = (target, time)


class AbortProcessError(Error):
    """中止处理"""

    def __init__(self, msg=""):
        Error.__init__(self, "Abort processing: %r" % msg)
        self.args = (msg,)


class PermissionDeniedError(Error):
    """对象无权限，结束处理"""

    def __init__(self, obj):
        Error.__init__(self, "Permission denied: %r" % obj)
        self.obj = obj
        self.args = (obj,)
