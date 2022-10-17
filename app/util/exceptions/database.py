from . import Error


class DatabaseManagerInitializedError(Error):
    """数据库管理器未初始化"""

    def __init__(self):
        Error.__init__(self, "DatabaseManager is not initialized")


class DatabaseManagerAlreadyInitializedError(Error):
    """数据库管理器重复初始化"""

    def __init__(self):
        Error.__init__(self, "DatabaseManager is already initialized")
