from . import Error


class AppCoreNotInitializedError(Error):
    """核心模块未初始化"""

    def __init__(self):
        Error.__init__(self, "AppCore is not initialized")


class AppCoreAlreadyInitializedError(Error):
    """核心模块重复初始化"""

    def __init__(self):
        Error.__init__(self, "AppCore is already initialized")


class AriadneAlreadyLaunchedError(Error):
    """Ariadne重复启动"""

    def __init__(self):
        Error.__init__(self, "Ariadne is already launched")
