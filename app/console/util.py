from loguru import logger


def unknown_error(msg=None):
    """未知错误默认回复消息"""
    send("未知错误\n" + msg or "")


def args_error(msg=None):
    """参数错误默认回复消息"""
    send(msg or "输入的参数错误！")


def arg_type_error():
    """类型错误默认回复消息"""
    send("参数类型错误！")


def exec_permission_error():
    """权限不够回复消息"""
    send("没有相应操作权限！")


def exec_success():
    send("指令执行成功！")


def send(resp):
    """回送消息"""
    logger.opt(raw=True).info((resp or "").strip("\n") + "\n\n" if resp else "\n")
