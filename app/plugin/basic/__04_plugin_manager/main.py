import asyncio
from typing import Union

from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.model import Friend, Member, Group
from graia.broadcast.interrupt.waiter import Waiter
from loguru import logger
from prettytable import PrettyTable

from app.core.commander import CommandDelegateManager
from app.core.exceptions import RemotePluginNotFound, LocalPluginNotFound
from app.core.plugins import PluginManager
from app.plugin.base import Plugin
from app.util.control import Permission, Switch
from app.util.decorator import permission_required
from app.util.text2image import create_image

manager: CommandDelegateManager = CommandDelegateManager.get_instance()
plugin_mgr: PluginManager = PluginManager.get_instance()


class AnswerWaiter(Waiter.create([FriendMessage, GroupMessage])):
    """等待回答"""

    def __init__(self, original: Plugin, event: str):
        self.message = None
        self.target = None
        self.sender = None
        self.original = original
        self.event = getattr(self, event)

    async def detected_event(self, target: Union[Friend, Member], sender: Union[Friend, Group], message: MessageChain):
        self.target = target
        self.sender = sender
        self.message = message.display
        if isinstance(self.target, Friend) and self.original.friend.id == self.target.id or \
                all([isinstance(self.target, Member), self.original.member.id == self.target.id,
                     self.original.group.id == self.sender.id]):
            result = await self.event()
            if result is not None:
                return result

    async def choose_event(self):
        if self.message.isdigit() and int(self.message) > 0:
            return self.message
        else:
            await self.original.app.send_message(self.sender, MessageChain([Plain('请输入对应序号')]))

    async def confirm_event(self):
        if self.message == '是':
            return True
        elif self.message == '否':
            return False
        else:
            await self.original.app.send_message(self.sender, MessageChain([Plain('请回答：是 / 否')]))


@permission_required(level=Permission.GROUP_ADMIN)
@manager.register(
    entry='plugin',
    brief_help='插件管理',
    alc=Alconna(
        headers=manager.headers,
        command='plugin',
        options=[
            Subcommand('open', help_text='开启插件, <plugin>插件英文名', args=Args['plugin', str, ...], options=[
                Option('--all|-a', help_text='开启全部插件'),
                Option('--friend|-f', help_text='针对好友开关(仅超级管理员可用)', args=Args['qq', int])
            ]),
            Subcommand('close', help_text='关闭插件, <plugin_cmd>插件触发命令', args=Args['plugin', str, ...], options=[
                Option('--all|-a', help_text='关闭全部插件'),
                Option('--friend|-f', help_text='针对好友开关(仅超级管理员可用)', args=Args['qq', int])
            ]),
            Subcommand('install', help_text='安装插件, <plugin>插件英文名', args=Args['plugin', str], options=[
                Option('--upgrade|-u', help_text='更新插件')
            ]),
            Subcommand('remove', help_text='删除插件, <plugin>插件英文名', args=Args['plugin', str]),
            Subcommand('list', help_text='列出本地插件', options=[
                Option('--remote|-m', help_text='列出仓库插件')
            ]),
            Subcommand('load', help_text='加载插件, <plugin>插件英文名', args=Args['plugin', str]),
            Subcommand('unload', help_text='卸载插件, <plugin>插件英文名', args=Args['plugin', str]),
            Subcommand('reload', help_text='重载插件[默认全部], <plugin>插件英文名', args=Args['plugin', str, 'all_plugin'])
        ],
        help_text='插件管理'
    )
)
async def process(self: Plugin, command: Arpamar, alc: Alconna):
    subcommand = command.subcommands
    if not subcommand:
        return await self.print_help(alc.get_help())
    try:
        resp = await master_admin_process(self, subcommand)
        if not resp:
            resp = await group_admin_process(self, subcommand, alc)
        return resp
    except ModuleNotFoundError as e:
        logger.error(f"插件加载失败: {e}")
        return MessageChain(Plain(f"插件加载失败: {e}"))
    except RemotePluginNotFound as e:
        logger.error(f"未在插件仓库找到该插件: {e}")
        return MessageChain(Plain(f"未在插件仓库找到该插件: {e}"))
    except LocalPluginNotFound:
        logger.error(f"本地未找到该插件")
        return MessageChain(Plain(f"本地未找到该插件"))
    except asyncio.TimeoutError:
        return MessageChain(Plain('等待超时'))
    except AssertionError:
        return self.args_error()
    except Exception as e:
        logger.exception(e)
        return self.unkown_error()


@permission_required(level=Permission.MASTER)
async def master_admin_process(self: Plugin, subcommand: dict):
    user = getattr(self, 'friend', None) or getattr(self, 'group', None)
    if install := subcommand.get("install"):
        plugin = install['plugin']
        upgrade = 'upgrade' in install

        if upgrade:  # 更新插件
            plugins = await plugin_mgr.get_plugin_info(plugin)
            if len(plugins) == 1:
                install_plugin = plugins[0]
            elif len(plugins) > 1:
                await self.app.send_message(user, MessageChain([
                    Plain(f"检测到本地存在多个{plugin}插件，请选择更新哪个："),
                    *[Plain(f"\n{i + 1}. {p['name']} - {p['author']}: {p['version']}") for i, p in enumerate(plugins)]
                ]))
                ret = await self.inc.wait(AnswerWaiter(self, 'choose_event'), timeout=60)
                if ret > len(plugins):
                    return self.args_error()
                install_plugin = plugins[ret - 1]
            else:
                return MessageChain(Plain(f"未在本地找到{plugin}插件"))
            if await plugin_mgr.find_plugin_exist(install_plugin['root_dir']):
                plugin_mgr.delete_plugin(install_plugin['root_dir'])
            await self.app.send_message(user, Plain('插件正在更新中...'))
        else:
            if plugins := await plugin_mgr.get_plugin_info(plugin):
                await self.app.send_message(user, MessageChain([
                    Plain(f"本地已存在下列插件: \n"),
                    Plain(
                        '\n'.join(
                            f"{i + 1}. {p['name']} - {p['author']}: {p['version']}" for i, p in enumerate(plugins))),
                    Plain(f"\n是否要继续安装（是/否）")
                ]))
                if not await self.inc.wait(AnswerWaiter(self, 'confirm_event'), timeout=30):
                    return MessageChain([Plain('取消安装')])

            install_plugin_list = []  # 记录可能的安装插件
            remote_plugin_list = await plugin_mgr.get_remote_plugins()  # 获取仓库插件
            for remote_plugin in remote_plugin_list:
                if remote_plugin['name'] == plugin:
                    install_plugin_list.append(remote_plugin)  # 将插件加入可能的安装列表
            if not install_plugin_list:
                raise RemotePluginNotFound(plugin)
            if len(install_plugin_list) == 1:
                install_plugin: dict = install_plugin_list[0]
            else:  # 如果有多个插件, 则提示用户选择
                msg = f"插件仓库中存在多个名为{plugin}的插件, 请选择一个插件安装"
                msg += '\n'.join(f"{i + 1}. {info['name']} - {info['author']}: {info['version']}" for i, info in
                                 enumerate(install_plugin_list))
                await self.app.send_message(user, MessageChain(msg))
                ret = await self.inc.wait(AnswerWaiter(self, 'choose_event'), timeout=60)
                if ret > len(install_plugin_list):
                    return self.args_error()
                install_plugin: dict = install_plugin_list[ret - 1]

            if await plugin_mgr.find_plugin_exist(install_plugin):
                return MessageChain([Plain('该插件已存在, 请使用 --upgrade 更新插件')])
            await self.app.send_message(user, Plain('插件正在安装中...'))

        await self.app.send_message(user, MessageChain(
            f"正在尝试安装插件: {install_plugin['name']} - {install_plugin['author']}"
        ))
        if await plugin_mgr.install_plugin(install_plugin):
            return MessageChain([
                Plain('插件升级成功: ' if upgrade else '插件安装成功: '),
                Plain(f"{install_plugin['name']} - {install_plugin['author']}")
            ])
        return MessageChain([
            Plain('插件安装失败，请重试: '),
            Plain(f"{install_plugin['name']} - {install_plugin['author']}")
        ])
    elif remove := subcommand.get("remove"):
        plugin = remove['plugin']
        plugins = await plugin_mgr.get_plugin_info(plugin)
        if len(plugins) == 1:
            delete_plugin = plugins[0]
        elif len(plugins) > 1:
            await self.app.send_message(user, MessageChain([
                Plain(f"检测到本地存在多个{plugin}插件，请选择删除哪个："),
                *[Plain(f"\n{i + 1}. {p['name']} - {p['author']}: {p['version']}") for i, p in enumerate(plugins)]
            ]))
            ret = await self.inc.wait(AnswerWaiter(self, 'choose_event'), timeout=60)
            if ret > len(plugins):
                return self.args_error()
            delete_plugin = plugins[ret - 1]
        else:
            return MessageChain(Plain(f"未在本地找到{plugin}插件"))
        plugin_mgr.delete_plugin(delete_plugin)
        return MessageChain([Plain(f"插件删除成功: {delete_plugin['name']} - {delete_plugin['author']}")])
    elif 'list' in subcommand:
        msg = PrettyTable()
        msg.field_names = ['序号', '插件名', '作者', '版本号', '介绍']
        if subcommand['list']:
            for index, plugin in enumerate(await plugin_mgr.get_remote_plugins()):
                msg.add_row([index + 1, plugin['name'], plugin['author'], plugin['version'], plugin['description']])
        else:
            for index, plugin in enumerate(await plugin_mgr.get_plugin_info('*')):
                msg.add_row([index + 1, plugin['name'], plugin['author'], plugin['version'], plugin['description']])
        msg.align = 'c'
        return MessageChain([Image(data_bytes=await create_image(msg.get_string(), cut=150))])
    elif load := subcommand.get("load"):
        plugin = load['plugin']
        plugins = await plugin_mgr.get_plugin_info(plugin)
        if len(plugins) == 1:
            load_plugin = plugins[0]
        elif len(plugins) > 1:
            await self.app.send_message(user, MessageChain([
                Plain(f"检测到本地存在多个{plugin}插件，请选择加载哪个："),
                *[Plain(f"\n{i + 1}. {p['name']} - {p['author']}: {p['version']}") for i, p in enumerate(plugins)]
            ]))
            ret = await self.inc.wait(AnswerWaiter(self, 'choose_event'), timeout=60)
            if ret > len(plugins):
                return self.args_error()
            load_plugin = plugins[ret - 1]
        else:
            return MessageChain(Plain(f"未在本地找到{plugin}插件"))
        await self.app.send_message(user, MessageChain(
            f"正在尝试加载插件: {load_plugin['name']} - {load_plugin['author']}"
        ))
        if await plugin_mgr.load_plugin(load_plugin):
            return MessageChain([
                Plain('插件加载成功: '),
                Plain(f"{load_plugin['name']} - {load_plugin['author']}")
            ])
        return MessageChain([
            Plain('插件加载失败，请重试: '),
            Plain(f"{load_plugin['name']} - {load_plugin['author']}")
        ])
    elif unloaded := subcommand.get("unload"):
        plugin = unloaded['plugin']
        plugins = await plugin_mgr.get_plugin_info(plugin)
        if len(plugins) == 1:
            unloaded_plugin = plugins[0]
        elif len(plugins) > 1:
            await self.app.send_message(user, MessageChain([
                Plain(f"检测到本地存在多个{plugin}插件，请选择卸载哪个："),
                *[Plain(f"\n{i + 1}. {p['name']} - {p['author']}: {p['version']}") for i, p in enumerate(plugins)]
            ]))
            ret = await self.inc.wait(AnswerWaiter(self, 'choose_event'), timeout=60)
            if ret > len(plugins):
                return self.args_error()
            unloaded_plugin = plugins[ret - 1]
        else:
            return MessageChain(Plain(f"未在本地找到{plugin}插件"))
        await self.app.send_message(user, MessageChain(
            f"正在尝试卸载插件: {unloaded_plugin['name']} - {unloaded_plugin['author']}"
        ))
        if plugin_mgr.unload_plugin(unloaded_plugin['root_dir']):
            return MessageChain([
                Plain('插件卸载成功: '),
                Plain(f"{unloaded_plugin['name']} - {unloaded_plugin['author']}")
            ])
        return MessageChain([
            Plain('该扩展插件未加载: '),
            Plain(f"{unloaded_plugin['name']} - {unloaded_plugin['author']}")
        ])
    elif reload := subcommand.get("reload"):
        plugin = reload['plugin']
        if plugin == 'all_plugin':
            plugin_mgr.reload_plugin()
            return MessageChain([Plain('所有插件重载成功')])
        else:
            plugins = await plugin_mgr.get_plugin_info(plugin)
            if len(plugins) == 1:
                reload_plugin = plugins[0]
            elif len(plugins) > 1:
                await self.app.send_message(user, MessageChain([
                    Plain(f"检测到本地存在多个{plugin}插件，请选择重载哪个："),
                    *[Plain(f"\n{i + 1}. {p['name']} - {p['author']}: {p['version']}") for i, p in enumerate(plugins)]
                ]))
                ret = await self.inc.wait(AnswerWaiter(self, 'choose_event'), timeout=60)
                if ret > len(plugins):
                    return self.args_error()
                reload_plugin = plugins[ret - 1]
            else:
                return MessageChain(Plain(f"未在本地找到{plugin}插件"))
            await self.app.send_message(user, MessageChain(
                f"正在尝试重载插件: {reload_plugin['name']} - {reload_plugin['author']}"
            ))
            if plugin_mgr.reload_plugin(reload_plugin['root_dir']):
                return MessageChain([
                    Plain('插件重载成功: '),
                    Plain(f"{reload_plugin['name']} - {reload_plugin['author']}")
                ])
            return MessageChain([
                Plain('插件重载失败，请重试: '),
                Plain(f"{reload_plugin['name']} - {reload_plugin['author']}")
            ])


async def group_admin_process(self: Plugin, subcommand: Arpamar.subcommands, alc: Alconna):
    async def change_plugin_status(user: int):
        if hasattr(self, 'group'):
            return await Switch.plugin(self.member, perm, self.group)
        else:
            if user > 0:
                return await Switch.plugin(self.friend.id, perm, user)
            return '缺少QQ号'

    perm = ''
    qq = 0
    if open_ := subcommand.get("open"):
        if frd := open_.get("friend"):
            qq: int = frd['qq']
        if 'all' in open_:
            perm = '*'
        elif open_['plugin']:
            for plg in manager.get_delegates().values():
                if open_['plugin'] == plg.entry:
                    perm = open_['plugin']
    elif close_ := subcommand.get("close"):
        if frd := close_.get("friend"):
            qq: int = frd['qq']
        if 'all' in close_:
            perm = '-'
        elif close_['plugin']:
            for plg in manager.get_delegates().values():
                if close_['plugin'] == plg.entry:
                    if close_['plugin'] == alc.command:
                        return MessageChain('禁止关闭本插件管理工具')
                    perm = '-' + close_['plugin']
            if not perm:
                return MessageChain("未找到该插件！")
    else:
        return self.args_error()
    if perm:
        return MessageChain([Plain(await change_plugin_status(qq))])
    else:
        return self.args_error()
