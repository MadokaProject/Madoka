from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image

from app.core.settings import config
from app.util.text2image import create_image


async def print_help(help_doc: str):
    return MessageChain([Image(data_bytes=await create_image(help_doc, 80))])


def unknown_error():
    """未知错误默认回复消息"""
    return MessageChain([Plain('未知错误，请联系管理员处理！')])


def args_error():
    """参数错误默认回复消息"""
    return MessageChain([Plain('输入的参数错误！')])


def index_error():
    """索引错误默认回复消息"""
    return MessageChain([Plain('索引超出范围！')])


def arg_type_error():
    """类型错误默认回复消息"""
    return MessageChain([Plain('参数类型错误！')])


def exec_permission_error():
    """权限不够回复消息"""
    return MessageChain([Plain('没有相应操作权限！')])


def point_not_enough():
    return MessageChain([Plain(f'你的{config.COIN_NAME}不足哦！')])


def not_admin():
    return MessageChain([Plain('你的权限不足，无权操作此命令！')])


def exec_success():
    return MessageChain([Plain('指令执行成功！')])
