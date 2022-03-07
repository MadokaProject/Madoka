import json
import os
import shutil
import urllib.request
from pathlib import Path

from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from loguru import logger
from pip import main as pip
from prettytable import PrettyTable

from app.api.doHttp import doHttpRequest
from app.core.appCore import AppCore
from app.core.command_manager import CommandManager
from app.plugin.base import Plugin
from app.util.control import Permission, Switch
from app.util.decorator import permission_required
from app.util.text2image import create_image
from app.util.tools import app_path


class Module(Plugin):
    entry = 'plugin'
    brief_help = '插件管理'
    manager: CommandManager = CommandManager.get_command_instance()
    base_url = "https://madokaproject.coding.net/p/p/d/plugins/git/raw/master/"
    folder_path = os.path.join(app_path(), f'plugin/extension/')

    async def get_plugin_list(self) -> dict:
        return json.loads(await doHttpRequest(self.base_url + 'list.json', method='get'))

    async def get_plugin_by_url(self, plugin_name, url_lists) -> bool:
        async def download(__url, __filepath):
            logger.info("Try downloading file: {}".format(__url))
            if Path(__filepath).exists():
                logger.info("File have already exist. skip")
            else:
                try:
                    urllib.request.urlretrieve(__url, filename=__filepath)
                except Exception as e:
                    logger.error(f"Error occurred when downloading file, error message: {e}")
                    return False
            return True

        if not await download(self.base_url + f'{plugin_name}/{plugin_name}.py',
                              self.folder_path + f'{plugin_name}.py'):
            return False
        for url in url_lists:
            Path(self.folder_path + plugin_name + '_res' + ''.join(f'/{i}' for i in url.split('/')[:-1])).mkdir(
                parents=True, exist_ok=True)
            filepath = self.folder_path + f'{plugin_name}_res/' + url
            if not await download(self.base_url + f'{plugin_name}/{url}', filepath):
                return False
        return True

    @permission_required(level=Permission.GROUP_ADMIN)
    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('open', help_text='开启插件, <plugin>插件英文名', args=Args['plugin': str: ''], options=[
                Option('--all', alias='-a', help_text='开启全部插件'),
                Option('--friend', alias='-f', help_text='针对好友开关(仅超级管理员可用)', args=Args['qq': int])
            ]),
            Subcommand('close', help_text='关闭插件, <plugin>插件英文名', args=Args['plugin': str: ''], options=[
                Option('--all', alias='-a', help_text='关闭全部插件'),
                Option('--friend', alias='-f', help_text='针对好友开关(仅超级管理员可用)', args=Args['qq': int])
            ]),
            Subcommand('install', help_text='安装插件, <plugin>插件英文名', args=Args['plugin': str], options=[
                Option('--upgrade', alias='-u', help_text='更新插件')
            ]),
            Subcommand('remove', help_text='删除插件, <plugin>插件英文名', args=Args['plugin': str]),
            Subcommand('list', help_text='列出本地插件', options=[
                Option('--all', alias='-a', help_text='列出插件库所有插件')
            ]),
            Subcommand('load', help_text='加载插件, <plugin>插件英文名', args=Args['plugin': str]),
            Subcommand('unload', help_text='卸载插件, <plugin>插件英文名', args=Args['plugin': str]),
            Subcommand('reload', help_text='重载插件[默认全部], <plugin>插件英文名', args=Args['plugin': str: 'all_plugin'])
        ],
        help_text='插件管理'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        other_args = command.other_args
        if not subcommand:
            return await self.print_help(alc.get_help())
        try:
            resp = await self.master_admin_process(subcommand, other_args)
            if not resp:
                resp = await self.group_admin_process(subcommand, other_args)
            return resp
        except ModuleNotFoundError as e:
            logger.error(f"插件加载失败: {e}")
            return MessageChain.create(Plain(f"插件加载失败: {e}"))
        except AssertionError:
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()

    @permission_required(level=Permission.MASTER)
    async def master_admin_process(self, subcommand: dict, other_args: dict):
        def delete(__core: AppCore, __plugin):
            """删除插件"""
            __core.unload_plugin(__plugin)
            Path(self.folder_path + f'{__plugin}.py').unlink(missing_ok=True)
            __dir = Path(self.folder_path + __plugin + '_res')
            if __dir.exists():
                shutil.rmtree(__dir)

        if subcommand.__contains__('install'):
            core: AppCore = AppCore.get_core_instance()
            plugin = other_args['plugin']
            upgrade = other_args.__contains__('upgrade')
            if upgrade:  # 更新插件
                delete(core, plugin)
            elif await core.fild_plugin(f'app.plugin.extension.{plugin}'):
                return MessageChain.create([Plain('该插件已安装')])
            plugin_list = await self.get_plugin_list()
            if plugin in plugin_list.keys():
                logger.info('正在尝试安装插件' + plugin_list[plugin]['name'])
                url_list = [i for i in plugin_list[plugin]['resource']]
                if plugin_list[plugin]['pypi']:
                    url_list.append('requirements.txt')
                if await self.get_plugin_by_url(plugin, url_list):
                    if plugin_list[plugin]['pypi']:
                        pip(['install', '-r', f'{self.folder_path}{plugin}_res/requirements.txt'])
                    await core.load_plugin(plugin)
                    logger.success('插件安装成功: ' + plugin)
                    return MessageChain.create([Plain(('插件升级成功: ' if upgrade else '插件安装成功: ') + plugin)])
                else:
                    logger.error('插件安装失败，请重试' + plugin_list[plugin]['name'])
                    return MessageChain.create([Plain('插件安装失败，请重试: ' + plugin)])
            else:
                logger.warning('未找到该插件' + plugin_list[plugin]['name'])
                return MessageChain.create([Plain('未找到该插件: ' + plugin)])
        elif subcommand.__contains__('remove'):
            plugin = other_args['plugin']
            if not Path(self.folder_path + f'{plugin}.py').exists():
                return MessageChain.create([Plain('该插件不存在: ' + plugin)])
            delete(AppCore.get_core_instance(), plugin)
            return MessageChain.create([Plain('插件删除成功: ' + plugin)])
        elif subcommand.__contains__('list'):
            if other_args.__contains__('all'):
                msg = PrettyTable()
                msg.field_names = ['序号', '插件名', '英文名', '作者', '版本号']
                for index, (name, plugin) in enumerate((await self.get_plugin_list()).items()):
                    msg.add_row([index + 1, plugin['name'], name, plugin['author'], plugin['version']])
                msg.align = 'c'
                return MessageChain.create([Image(data_bytes=await create_image(msg.get_string()))])
            msg = PrettyTable()
            msg.field_names = ['序号', '英文名']
            core: AppCore = AppCore.get_core_instance()
            for index, name in enumerate(core.get_plugin()):
                msg.add_row([index + 1, name.__name__.split('.')[-1]])
            msg.align = 'c'
            return MessageChain.create([Image(data_bytes=await create_image(msg.get_string()))])
        elif subcommand.__contains__('load'):
            core: AppCore = AppCore.get_core_instance()
            return MessageChain.create([Plain(await core.load_plugin(other_args['plugin']))])
        elif subcommand.__contains__('unload'):
            core: AppCore = AppCore.get_core_instance()
            return MessageChain.create([Plain(core.unload_plugin(other_args['plugin']))])
        elif subcommand.__contains__('reload'):
            core: AppCore = AppCore.get_core_instance()
            return MessageChain.create([Plain(core.reload_plugin_modules(other_args['plugin']))])

    async def group_admin_process(self, subcommand: dict, other_args: dict):
        async def change_plugin_status():
            if hasattr(self, 'group'):
                return await Switch.plugin(self.member, perm, self.group)
            else:
                if other_args.__contains__('qq'):
                    user = other_args['qq']
                else:
                    return '缺少QQ号'
                return await Switch.plugin(self.friend.id, perm, user)

        perm = ''
        if subcommand.__contains__('open'):
            if other_args.__contains__('all'):
                perm = '*'
            elif other_args['plugin'] != '':
                core: AppCore = AppCore.get_core_instance()
                for plugin in core.get_plugin():
                    if other_args['plugin'] == plugin.Module.entry:  # plugin.Module(self.message).entry:
                        perm = other_args['plugin']
        elif subcommand.__contains__('close'):
            if other_args.__contains__('all'):
                perm = '-'
            elif other_args['plugin'] != '':
                core: AppCore = AppCore.get_core_instance()
                for plugin in core.get_plugin():
                    if other_args['plugin'] == plugin.Module.entry:
                        if other_args['plugin'] == 'plugin':
                            return MessageChain.create([Plain('禁止关闭本插件管理工具')])
                        perm = '-' + other_args['plugin']
        if perm:
            return MessageChain.create([Plain(await change_plugin_status())])
        else:
            return self.args_error()
