from . import Error


class DependError(Error):
    pass


class NotActivatedError(DependError):
    """未激活用户"""

    def __init__(self, obj):
        Error.__init__(self, "%r is inactivated" % obj)
        self.obj = obj
        self.args = (obj,)


class BannedError(DependError):
    """黑名单用户"""

    def __init__(self, obj):
        Error.__init__(self, "%r is banned" % obj)
        self.obj = obj
        self.args = (obj,)
