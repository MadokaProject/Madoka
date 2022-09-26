from app.core.settings import config
from app.util.graia import Image, Plain, message
from app.util.text2image import create_image


async def print_help(sender, help_doc: str):
    message([Image(data_bytes=await create_image(help_doc, 80))]).target(sender).send()


def unknown_error(sender):
    """未知错误默认回复消息"""
    message([Plain("未知错误，请联系管理员处理！")]).target(sender).send()


def args_error(sender):
    """参数错误默认回复消息"""
    message([Plain("输入的参数错误！")]).target(sender).send()


def index_error(sender):
    """索引错误默认回复消息"""
    message([Plain("索引超出范围！")]).target(sender).send()


def arg_type_error(sender):
    """类型错误默认回复消息"""
    message([Plain("参数类型错误！")]).target(sender).send()


def exec_permission_error(sender):
    """权限不够回复消息"""
    message([Plain("没有相应操作权限！")]).target(sender).send()


def point_not_enough(sender):
    message([Plain(f"你的{config.COIN_NAME}不足哦！")]).target(sender).send()


def not_admin(sender):
    message([Plain("你的权限不足，无权操作此命令！")]).target(sender).send()


def exec_success(sender):
    message([Plain("指令执行成功！")]).target(sender).send()
