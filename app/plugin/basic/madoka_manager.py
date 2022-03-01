import json
import os
import shutil
import urllib.request
from pathlib import Path

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from loguru import logger
from pip import main as pip
from prettytable import PrettyTable

from app.api.doHttp import doHttpRequest
from app.core.appCore import AppCore
from app.plugin.base import Plugin
from app.util.control import Permission, Switch
from app.util.decorator import permission_required
from app.util.text2image import create_image
from app.util.tools import isstartswith, app_path


class Module(Plugin):
    entry = ['.plugin', '.插件']
    brief_help = '插件管理'
    full_help = {
        '开启, open': {
            '开启插件': '',
            '[plugin]': '插件英文名'
        },
        '关闭, close': {
            '关闭插件': '',
            '[plugin]': '插件英文名'
        },
        '安装, install': {
            '安装插件': '',
            '[plugin]': '插件英文名'
        },
        '删除, remove': {
            '删除插件': '',
            '[plugin]': '插件英文名'
        },
        '插件大全, listall': '列出插件库所有插件',
        '本地插件, list': '列出本地插件',
        '加载, load': {
            '加载插件': '',
            '[plugin]': '插件英文名'
        },
        '卸载, unload': {
            '卸载插件': '',
            '[plugin]': '插件英文名'
        },
        '重载, reload': {
            '重载插件': '',
            '[plugin]': '插件英文名(不指定时重载所有插件)'
        }
    }
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
    async def process(self):
        if not self.msg:
            await self.print_help()
            return
        try:
            await self.master_admin_process()
            if not self.resp:
                await self.group_admin_process()
        except ModuleNotFoundError as e:
            self.resp = MessageChain.create(Plain(f"插件加载失败: {e}"))
            logger.error(f"插件加载失败: {e}")
        except AssertionError:
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()

    @permission_required(level=Permission.MASTER)
    async def master_admin_process(self):
        if isstartswith(self.msg[0], ['安装', 'install']):
            assert len(self.msg) == 2
            core: AppCore = AppCore.get_core_instance()
            if await core.fild_plugin(f'app.plugin.extension.{self.msg[1]}'):
                self.resp = MessageChain.create([Plain('该插件已安装')])
                return
            plugin_list = await self.get_plugin_list()
            if self.msg[1] in plugin_list.keys():
                logger.info('正在尝试安装插件' + plugin_list[self.msg[1]]['name'])
                url_list = [i for i in plugin_list[self.msg[1]]['resource']]
                if plugin_list[self.msg[1]]['pypi']:
                    url_list.append('requirements.txt')
                if await self.get_plugin_by_url(self.msg[1], url_list):
                    if plugin_list[self.msg[1]]['pypi']:
                        pip(['install', '-r', f'{self.folder_path}{self.msg[1]}_res/requirements.txt'])
                    await core.load_plugin(self.msg[1])
                    self.resp = MessageChain.create([Plain('插件安装成功: ' + self.msg[1])])
                    logger.success('插件安装成功: ' + self.msg[1])
                else:
                    self.resp = MessageChain.create([Plain('插件安装失败，请重试: ' + self.msg[1])])
                    logger.error('插件安装失败，请重试' + plugin_list[self.msg[1]]['name'])
            else:
                self.resp = MessageChain.create([Plain('未找到该插件: ' + self.msg[1])])
                logger.warning('未找到该插件' + plugin_list[self.msg[1]]['name'])
        elif isstartswith(self.msg[0], ['删除', 'remove']):
            assert len(self.msg) == 2
            if not Path(self.folder_path + f'{self.msg[1]}.py').exists():
                self.resp = MessageChain.create([Plain('该插件不存在: ' + self.msg[1])])
                return
            core: AppCore = AppCore.get_core_instance()
            core.unload_plugin(self.msg[1])
            Path(self.folder_path + f'{self.msg[1]}.py').unlink()
            __dir = Path(self.folder_path + self.msg[1] + '_res')
            if __dir.exists():
                shutil.rmtree(__dir)
            self.resp = MessageChain.create([Plain('插件删除成功: ' + self.msg[1])])
        elif isstartswith(self.msg[0], ['插件大全', 'listall'], full_match=1):
            msg = PrettyTable()
            msg.field_names = ['序号', '插件名', '英文名', '作者', '版本号']
            for index, (name, plugin) in enumerate((await self.get_plugin_list()).items()):
                msg.add_row([index + 1, plugin['name'], name, plugin['author'], plugin['version']])
            msg.align = 'c'
            self.resp = MessageChain.create([
                Image(data_bytes=(await create_image(msg.get_string())).getvalue())
            ])
        elif isstartswith(self.msg[0], ['本地插件', 'list'], full_match=1):
            msg = PrettyTable()
            msg.field_names = ['序号', '英文名']
            core: AppCore = AppCore.get_core_instance()
            for index, name in enumerate(core.get_plugin()):
                msg.add_row([index + 1, name.__name__.split('.')[-1]])
            msg.align = 'c'
            self.resp = MessageChain.create([
                Image(data_bytes=(await create_image(msg.get_string())).getvalue())
            ])
        elif isstartswith(self.msg[0], ['加载', 'load']):
            assert len(self.msg) == 2
            core: AppCore = AppCore.get_core_instance()
            self.resp = MessageChain.create([Plain(await core.load_plugin(self.msg[1]))])
        elif isstartswith(self.msg[0], ['卸载', 'unload']):
            assert len(self.msg) == 2
            core: AppCore = AppCore.get_core_instance()
            self.resp = MessageChain.create([Plain(core.unload_plugin(self.msg[1]))])
        elif isstartswith(self.msg[0], ['重载', 'reload']):
            plugin = self.msg[1] if len(self.msg) == 2 else None
            core: AppCore = AppCore.get_core_instance()
            self.resp = MessageChain.create([Plain(core.reload_plugin_modules(plugin))])

    async def group_admin_process(self):
        async def change_plugin_status():
            if hasattr(self, 'group'):
                return await Switch.plugin(self.member, perm, self.group)
            elif len(self.msg) == 3:
                return await Switch.plugin(self.friend.id, perm, int(self.msg[2]))

        perm = ''
        if isstartswith(self.msg[0], ['开启', 'open']):
            assert len(self.msg) >= 2
            if isstartswith(self.msg[1], ['all', '全部']):
                perm = '*'
            else:
                core: AppCore = AppCore.get_core_instance()
                for plugin in core.get_plugin():
                    if self.msg[1] == plugin.Module(self.message).entry[0][1:]:
                        perm = self.msg[1]
        elif isstartswith(self.msg[0], ['关闭', 'close']):
            assert len(self.msg) >= 2
            if isstartswith(self.msg[1], ['all', '全部']):
                perm = '-'
            else:
                core: AppCore = AppCore.get_core_instance()
                for plugin in core.get_plugin():
                    if self.msg[1] == plugin.Module(self.message).entry[0][1:]:
                        if self.msg[1] == 'plugin':
                            self.resp = MessageChain.create([Plain('禁止关闭本插件管理工具')])
                            return
                        perm = '-' + self.msg[1]
        if perm:
            self.resp = MessageChain.create([Plain(await change_plugin_status())])
        else:
            self.args_error()
