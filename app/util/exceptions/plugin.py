from . import Error


class PluginManagerInitializedError(Error):
    """插件管理器未初始化"""

    def __init__(self):
        Error.__init__(self, "PluginManager is not initialized")


class PluginManagerAlreadyInitializedError(Error):
    """插件管理器重复初始化"""

    def __init__(self):
        Error.__init__(self, "PluginManager is already initialized")


class PluginNotInitializedError(Error):
    """插件未加载"""

    def __init(self, name):
        Error.__init__(self, "Plugin %r is not initialized" % name)
        self.name = name
        self.args = (name,)


class NonStandardPluginError(Error):
    """非标准插件"""

    def __init__(self, name):
        Error.__init__(self, "Plugin %r is not standard" % name)
        self.name = name
        self.args = (name,)


class RemotePluginNotFoundError(Error):
    """未在插件仓库找到该插件"""

    def __init__(self, name):
        Error.__init__(self, "Remote plugin %r not found" % name)
        self.name = name
        self.args = (name,)


class LocalPluginNotFoundError(Error):
    """未在本地找到该插件"""

    def __init__(self, name):
        Error.__init__(self, "Local plugin %r not found" % name)
        self.name = name
        self.args = (name,)
