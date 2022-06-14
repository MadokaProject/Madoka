from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from loguru import logger
from prettytable import PrettyTable

from app.core.commander import CommandDelegateManager
from app.core.exceptions import RemotePluginNotFound
from app.core.plugins import PluginManager
from app.plugin.base import Plugin
from app.util.control import Permission, Switch
from app.util.decorator import permission_required
from app.util.text2image import create_image

manager: CommandDelegateManager = CommandDelegateManager.get_instance()
plugin_mgr: PluginManager = PluginManager.get_instance()


@permission_required(level=Permission.GROUP_ADMIN)
@manager.register(
    entry='plugin',
    brief_help='插件管理',
    alc=Alconna(
        headers=manager.headers,
        command='plugin',
        options=[
            Subcommand('open', help_text='开启插件, <plugin>插件英文名', args=Args['plugin': str: ...], options=[
                Option('--all|-a', help_text='开启全部插件'),
                Option('--friend|-f', help_text='针对好友开关(仅超级管理员可用)', args=Args['qq': int])
            ]),
            Subcommand('close', help_text='关闭插件, <plugin_cmd>插件触发命令', args=Args['plugin': str: ...], options=[
                Option('--all|-a', help_text='关闭全部插件'),
                Option('--friend|-f', help_text='针对好友开关(仅超级管理员可用)', args=Args['qq': int])
            ]),
            Subcommand('install', help_text='安装插件, <plugin>插件英文名', args=Args['plugin': str], options=[
                Option('--upgrade|-u', help_text='更新插件')
            ]),
            Subcommand('remove', help_text='删除插件, <plugin>插件英文名', args=Args['plugin': str]),
            Subcommand('list', help_text='列出本地插件', options=[
                Option('--remote|-m', help_text='列出仓库插件')
            ]),
            Subcommand('load', help_text='加载插件, <plugin>插件英文名', args=Args['plugin': str]),
            Subcommand('unload', help_text='卸载插件, <plugin>插件英文名', args=Args['plugin': str]),
            Subcommand('reload', help_text='重载插件[默认全部], <plugin>插件英文名', args=Args['plugin': str: 'all_plugin'])
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
        return MessageChain.create(Plain(f"插件加载失败: {e}"))
    except RemotePluginNotFound as e:
        logger.error(f"未在插件仓库找到该插件: {e}")
        return MessageChain.create(Plain(f"未在插件仓库找到该插件: {e}"))
    except AssertionError:
        return self.args_error()
    except Exception as e:
        logger.exception(e)
        return self.unkown_error()


@permission_required(level=Permission.MASTER)
async def master_admin_process(self: Plugin, subcommand: dict):
    if install := subcommand.get("install"):
        plugin = install['plugin']
        upgrade = 'upgrade' in install
        if upgrade:  # 更新插件
            plugin_mgr.delete_plugin(plugin)
        elif await plugin_mgr.find_plugin(f'app.plugin.extension.{plugin}'):
            return MessageChain.create([Plain('该插件已安装')])
        await self.app.sendMessage(
            getattr(self, 'friend', None) or getattr(self, 'group', None),
            MessageChain.create(f'正在尝试安装插件: {plugin}')
        )
        if await plugin_mgr.install_plugin(plugin):
            return MessageChain.create([Plain(('插件升级成功: ' if upgrade else '插件安装成功: ') + plugin)])
        return MessageChain.create([Plain('插件安装失败，请重试: ' + plugin)])
    elif remove := subcommand.get("remove"):
        plugin = remove['plugin']
        if plugin_mgr.delete_plugin(plugin):
            return MessageChain.create([Plain('插件删除成功: ' + plugin)])
        return MessageChain.create([Plain('该插件不存在: ' + plugin)])
    elif 'list' in subcommand:
        if subcommand['list']:
            msg = PrettyTable()
            msg.field_names = ['序号', '插件名', '英文名', '作者', '版本号']
            for index, (name, plugin) in enumerate((await plugin_mgr.get_remote_plugins()).items()):
                msg.add_row([index + 1, plugin['name'], name, plugin['author'], plugin['version']])
            msg.align = 'c'
            return MessageChain.create([Image(data_bytes=await create_image(msg.get_string()))])
        msg = PrettyTable()
        msg.field_names = ['序号', '英文名']
        for index, name in enumerate(plugin_mgr.get_plugins().keys()):
            msg.add_row([index + 1, name.split('.')[-1]])
        msg.align = 'c'
        return MessageChain.create([Image(data_bytes=await create_image(msg.get_string()))])
    elif load := subcommand.get("load"):
        if await plugin_mgr.load_plugin(load['plugin']):
            return MessageChain.create(f"加载扩展插件成功: {load['plugin']}")
        return MessageChain.create(f"扩展插件加载失败: {load['plugin']}")
    elif unloaded := subcommand.get("unload"):
        if plugin_mgr.unload_plugin(unloaded['plugin']):
            return MessageChain.create(f"卸载扩展插件成功: {unloaded['plugin']}")
        return MessageChain.create(f"该扩展插件未加载: {unloaded['plugin']}")
    elif reload := subcommand.get("reload"):
        if plugin_mgr.reload_plugin(reload['plugin']):
            return MessageChain.create('重载成功')
        return MessageChain.create('重载失败，无此插件！')


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
                        return MessageChain.create('禁止关闭本插件管理工具')
                    perm = '-' + close_['plugin']
            if not perm:
                return MessageChain.create("未找到该插件！")
    else:
        return self.args_error()
    if perm:
        return MessageChain.create([Plain(await change_plugin_status(qq))])
    else:
        return self.args_error()
