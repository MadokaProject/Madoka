import asyncio
from textwrap import fill
from typing import Dict, Optional, Union

from loguru import logger
from prettytable import PrettyTable

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.core.exceptions import LocalPluginNotFoundError, RemotePluginNotFoundError
from app.core.plugins import PluginManager
from app.util.alconna import Args, Arpamar, Commander, Option, Subcommand
from app.util.control import Permission, Switch
from app.util.graia import (
    Ariadne,
    Friend,
    FriendMessage,
    GraiaScheduler,
    Group,
    GroupMessage,
    Image,
    InterruptControl,
    Member,
    MessageChain,
    Plain,
    Waiter,
    message,
    timers,
)
from app.util.phrases import args_error
from app.util.text2image import create_image

core: AppCore = AppCore()
app: Ariadne = core.get_app()
sche: GraiaScheduler = core.get_scheduler()
manager: CommandDelegateManager = CommandDelegateManager()
plugin_mgr: PluginManager = PluginManager()


class AnswerWaiter(Waiter.create([FriendMessage, GroupMessage])):
    """等待回答"""

    def __init__(self, target: Union[Friend, Member], sender: Union[Friend, Group], event: str):
        self.message = None
        self.target = target
        self.sender = sender
        self.event = getattr(self, event)

    async def detected_event(
        self,
        target: Union[Friend, Member],
        sender: Union[Friend, Group],
        _message: MessageChain,
    ):
        self.message = _message.display
        if all([target == self.target, sender == self.sender]):
            result = await self.event()
            if result is not None:
                return result

    async def choose_event(self):
        if self.message.isdigit() and int(self.message) > 0:
            return self.message
        else:
            message("请输入对应序号").target(self.sender).send()

    async def confirm_event(self):
        if self.message == "是":
            return True
        elif self.message == "否":
            return False
        else:
            message("请回答：是 / 否").target(self.sender).send()


command = Commander(
    "plugin",
    "插件管理",
    Subcommand(
        "on",
        help_text="开启插件, <plugin_cmd>插件触发命令",
        args=Args["plugin;O", str],
        options=[
            Option("--all|-a", help_text="开启全部插件"),
            Option("--friend|-f", help_text="针对好友开关(仅超级管理员可用)", args=Args["qq", int]),
        ],
    ),
    Subcommand(
        "off",
        help_text="关闭插件, <plugin_cmd>插件触发命令",
        args=Args["plugin;O", str],
        options=[
            Option("--all|-a", help_text="关闭全部插件"),
            Option("--friend|-f", help_text="针对好友开关(仅超级管理员可用)", args=Args["qq", int]),
        ],
    ),
    Subcommand(
        "install",
        help_text="安装插件, <plugin>插件名",
        args=Args["plugin", str],
        options=[Option("--upgrade|-u", help_text="更新插件")],
    ),
    Subcommand("remove", help_text="删除插件, <plugin>插件名", args=Args["plugin", str]),
    Subcommand("list", help_text="列出本地插件", options=[Option("--remote|-m", help_text="列出仓库插件")]),
    Subcommand("load", help_text="加载插件, <plugin>插件名", args=Args["plugin", str]),
    Subcommand("unload", help_text="卸载插件, <plugin>插件名", args=Args["plugin", str]),
    Subcommand("reload", help_text="重载插件[默认全部], <plugin>插件名", args=Args["plugin", str, "all_plugin"]),
    Subcommand("check", help_text="检查插件更新"),
)


async def choose_plugin(
    target: Union[Friend, Member], sender: Union[Friend, Group], inc: InterruptControl, plugin: str
) -> Optional[Dict[str, str]]:
    """选择插件"""
    plugins = await plugin_mgr.get_info(plugin)
    if len(plugins) == 1:
        return plugins[0]
    elif len(plugins) > 1:
        message(
            [
                Plain(f"检测到本地存在多个{plugin}插件，请选择："),
                *[Plain(f"\n{i + 1}. {p['name']} - {p['author']}: {p['version']}") for i, p in enumerate(plugins)],
            ]
        ).target(sender).send()
        ret = await inc.wait(AnswerWaiter(target, sender, "choose_event"), timeout=60)
        if ret > len(plugins):
            raise IndexError("序号超出范围")
        return plugins[ret - 1]


@command.parse("install", permission=Permission.MASTER)
async def install(target: Union[Friend, Member], sender: Union[Friend, Group], inc: InterruptControl, cmd: Arpamar):
    plugin = cmd.query("plugin")
    upgrade = bool(cmd.query("install.upgrade"))

    try:
        if upgrade:  # 更新插件
            install_plugin = await choose_plugin(target, sender, inc, plugin)
            if not install_plugin:
                return message(f"未在本地找到{plugin}插件").target(sender).send()

            for remote_plugin in await plugin_mgr.get_remote_info():
                if (
                    remote_plugin["name"] == install_plugin["name"]
                    and remote_plugin["root_dir"] == install_plugin["root_dir"]
                ):
                    install_plugin = remote_plugin
                    break
            else:
                raise RemotePluginNotFoundError(plugin)

            if await plugin_mgr.exist(install_plugin):
                plugin_mgr.delete(install_plugin)
            message("插件正在更新中...").target(sender).send()
        else:
            if plugins := await plugin_mgr.get_info(plugin):
                message(
                    [
                        Plain("本地已存在下列插件: \n"),
                        *[
                            Plain(f"\n{i + 1}. {p['name']} - {p['author']}: {p['version']}")
                            for i, p in enumerate(plugins)
                        ],
                        Plain("\n是否要继续安装（是/否）"),
                    ]
                ).target(sender).send()
                if not await inc.wait(AnswerWaiter(target, sender, "confirm_event"), timeout=30):
                    return message("取消安装").target(sender).send()

            remote_plugin_list = await plugin_mgr.get_remote_info()  # 获取仓库插件
            install_plugin_list = [
                remote_plugin for remote_plugin in remote_plugin_list if remote_plugin["name"] == plugin
            ]

            if not install_plugin_list:
                raise RemotePluginNotFoundError(plugin)
            if len(install_plugin_list) == 1:
                install_plugin: dict = install_plugin_list[0]
            else:  # 如果有多个插件, 则提示用户选择
                msg = f"插件仓库中存在多个名为{plugin}的插件, 请选择一个插件安装"
                msg += "\n".join(
                    f"{i + 1}. {info['name']} - {info['author']}: {info['version']}"
                    for i, info in enumerate(install_plugin_list)
                )
                message(msg).target(sender).send()
                ret = await inc.wait(AnswerWaiter(target, sender, "choose_event"), timeout=60)
                if ret > len(install_plugin_list):
                    return args_error(sender)
                install_plugin: dict = install_plugin_list[ret - 1]

            if await plugin_mgr.exist(install_plugin):
                return message("该插件已存在, 请使用 --upgrade 更新插件").target(sender).send()
            message("插件正在安装中...").target(sender).send()

        message(f"正在尝试安装插件: {install_plugin['name']} - {install_plugin['author']}").target(sender).send()
        if await plugin_mgr.install(install_plugin):
            message(
                [
                    Plain("插件升级成功: " if upgrade else "插件安装成功: "),
                    Plain(f"{install_plugin['name']} - {install_plugin['author']}"),
                ]
            ).target(sender).send()
        else:
            message(
                [
                    Plain("插件安装失败，请重试: "),
                    Plain(f"{install_plugin['name']} - {install_plugin['author']}"),
                ]
            ).target(sender).send()
    except RemotePluginNotFoundError as e:
        logger.error(e)
        return message(f"未在插件仓库找到该插件: {e.name}").target(sender).send()
    except LocalPluginNotFoundError as e:
        logger.error(e)
        return message(f"未在本地找到该插件: {e.name}").target(sender).send()
    except asyncio.TimeoutError:
        return message("等待超时").target(sender).send()
    except IndexError:
        return args_error(sender)


@command.parse("remove", permission=Permission.MASTER)
async def remove(target: Union[Friend, Member], sender: Union[Friend, Group], inc: InterruptControl, cmd: Arpamar):
    try:
        plugin = cmd.query("plugin")
        delete_plugin = await choose_plugin(target, sender, inc, plugin)
        if not delete_plugin:
            return message(f"未在本地找到{plugin}插件").target(sender).send()
        plugin_mgr.delete(delete_plugin)
        return message(f"插件删除成功: {delete_plugin['name']} - {delete_plugin['author']}").target(sender).send()
    except IndexError:
        return args_error(sender)
    except asyncio.TimeoutError:
        return message("等待超时").target(sender).send()


@command.parse("list", permission=Permission.GROUP_ADMIN)
async def list_plugin(sender: Union[Friend, Group], cmd: Arpamar):
    msg = PrettyTable()
    msg.field_names = ["序号", "插件名", "作者", "版本号", "介绍"]
    if cmd.find("list.remote"):
        for index, plugin in enumerate(await plugin_mgr.get_remote_info()):
            msg.add_row(
                [
                    index + 1,
                    plugin["name"],
                    plugin["author"],
                    plugin["version"],
                    fill(plugin["description"], width=15),
                ]
            )
    else:
        for index, plugin in enumerate(await plugin_mgr.get_info("*")):
            msg.add_row(
                [
                    index + 1,
                    plugin["name"],
                    plugin["author"],
                    plugin["version"],
                    fill(plugin["description"], width=15),
                ]
            )
    msg.align = "c"
    return message([Image(data_bytes=await create_image(msg.get_string(), cut=150))]).target(sender).send()


@command.parse("load", permission=Permission.MASTER)
async def load(target: Union[Friend, Member], sender: Union[Friend, Group], inc: InterruptControl, cmd: Arpamar):
    try:
        plugin = cmd.query("plugin")
        load_plugin = await choose_plugin(target, sender, inc, plugin)
        if not load_plugin:
            return message(f"未在本地找到{plugin}插件").target(sender).send()
        message(f"正在尝试加载插件: {load_plugin['name']} - {load_plugin['author']}").target(sender).send()
        if await plugin_mgr.load(load_plugin):
            return message(f"插件加载成功: {load_plugin['name']} - {load_plugin['author']}").target(sender).send()
        return message(f"插件加载失败，请重试: {load_plugin['name']} - {load_plugin['author']}").target(sender).send()
    except IndexError:
        return args_error(sender)
    except asyncio.TimeoutError:
        return message("等待超时").target(sender).send()
    except ModuleNotFoundError as e:
        logger.error(f"插件加载失败: {e}")
        return message(f"插件加载失败: {e}").target(sender).send()


@command.parse("unload", permission=Permission.MASTER)
async def unload(target: Union[Friend, Member], sender: Union[Friend, Group], inc: InterruptControl, cmd: Arpamar):
    try:
        plugin = cmd.query("plugin")
        unload_plugin = await choose_plugin(target, sender, inc, plugin)
        if not unload_plugin:
            return message(f"未在本地找到{plugin}插件").target(sender).send()
        message(f"正在尝试卸载插件: {unload_plugin['name']} - {unload_plugin['author']}").target(sender).send()
        if plugin_mgr.unload(unload_plugin["root_dir"]):
            return message(f"插件卸载成功: {unload_plugin['name']} - {unload_plugin['author']}").target(sender).send()
        return message(f"该扩展插件未加载: {unload_plugin['name']} - {unload_plugin['author']}").target(sender).send()
    except IndexError:
        return args_error(sender)
    except asyncio.TimeoutError:
        return message("等待超时").target(sender).send()


@command.parse("reload", permission=Permission.MASTER)
async def reload(target: Union[Friend, Member], sender: Union[Friend, Group], inc: InterruptControl, cmd: Arpamar):
    try:
        plugin = cmd.query("plugin")
        if plugin == "all_plugin":
            plugin_mgr.reload()
            return message("所有插件重载成功").target(sender).send()
        else:
            reload_plugin = await choose_plugin(target, sender, inc, plugin)
            if not reload_plugin:
                return message(f"未在本地找到{plugin}插件").target(sender).send()
            message(f"正在尝试重载插件: {reload_plugin['name']} - {reload_plugin['author']}").target(sender).send()
            if plugin_mgr.reload(reload_plugin["root_dir"]):
                return message(f"插件重载成功: {reload_plugin['name']} - {reload_plugin['author']}").target(sender).send()
            return message(f"插件重载失败，请重试: {reload_plugin['name']} - {reload_plugin['author']}").target(sender).send()
    except IndexError:
        return args_error(sender)
    except asyncio.TimeoutError:
        return message("等待超时").target(sender).send()
    except ModuleNotFoundError as e:
        logger.error(f"插件加载失败: {e}")
        return message(f"插件加载失败: {e}").target(sender).send()


@command.parse("check", permission=Permission.MASTER)
async def check(sender: Union[Friend, Group]):
    if msg := await plugin_mgr.check_update():
        return message([Plain("检测到插件更新"), Image(data_bytes=msg)]).target(sender).send()
    return message("没有检测到插件更新").target(sender).send()


@command.parse("on", permission=Permission.GROUP_ADMIN)
async def on(target: Union[Friend, Member], sender: Union[Friend, Group], cmd: Arpamar):
    perm = ""
    _target = None
    if cmd.find("on.friend"):
        _target = cmd.query("qq")
    elif isinstance(sender, Group):
        _target = sender
    if cmd.find("on.all"):
        perm = "*"
    elif plugin := cmd.query("plugin"):
        for plg in manager.get_delegates().values():
            if plugin == plg.entry:
                perm = plugin
                break
    else:
        return args_error(sender)
    return (
        message(await Switch.plugin(target, perm, _target)).target(sender).send()
        if _target
        else message("缺少QQ号").target(sender).send()
    )


@command.parse("off", permission=Permission.GROUP_ADMIN)
async def off(target: Union[Friend, Member], sender: Union[Friend, Group], cmd: Arpamar):
    perm = ""
    _target = None
    if cmd.find("off.friend"):
        _target = cmd.query("qq")
    elif isinstance(sender, Group):
        _target = sender
    if cmd.find("off.all"):
        perm = "-"
    elif plugin := cmd.query("plugin"):
        for plg in manager.get_delegates().values():
            if plugin == plg.entry:
                if plugin == command.alconna.command:
                    return message("禁止关闭本插件管理工具").target(sender).send()
                perm = f"-{plugin}"
        if not perm:
            return message("未找到该插件！").target(sender).send()
    else:
        return args_error(sender)
    return (
        message(await Switch.plugin(target, perm, _target)).target(sender).send()
        if _target
        else message("缺少QQ号").target(sender).send()
    )


# 检查插件更新
@sche.schedule(timers.crontabify("30 7 * * * 0"))
async def check_plugin_update_tasker():
    if msg := await plugin_mgr.check_update():
        message(
            [
                Plain("检测到下列插件有更新啦~\n"),
                Image(data_bytes=msg),
            ]
        ).target(Config.master_qq).send()
