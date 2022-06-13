class CommandManagerInitialized(Exception):
    """命令管理器未初始化"""
    pass


class CommandManagerAlreadyInitialized(Exception):
    """命令管理器重复初始化"""
    pass


class AppCoreNotInitialized(Exception):
    """核心模块未初始化"""
    pass


class AppCoreAlreadyInitialized(Exception):
    """核心模块重复初始化"""
    pass


class AriadneAlreadyLaunched(Exception):
    """Ariadne重复启动"""
    pass


class PluginNotInitialized(Exception):
    """插件未加载"""
    pass


class AsyncioTasksGetResult(Exception):
    """task得到结果提前结束"""
    pass


class FrequencyLimitExceeded(Exception):
    """群组请求超出负载权重限制"""
    pass


class FrequencyLimitExceededAddBlackList(Exception):
    """单人请求超出负载权重限制并加入黑名单"""
    pass


class FrequencyLimitExceededDoNothing(Exception):
    """请求者在黑名单中不作回应"""
    pass


class NonStandardPlugin(Exception):
    """非标准插件"""
    pass


class PluginManagerInitialized(Exception):
    """插件管理器未初始化"""
    pass


class PluginManagerAlreadyInitialized(Exception):
    """插件管理器重复初始化"""
    pass


class RemotePluginNotFound(Exception):
    """未在插件仓库找到该插件"""
    pass
