import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp.client
import requests
from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.context import enter_context
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.util.doHttp import do_http_request
from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.core.settings import REPO
from app.plugin.base import Plugin, Scheduler
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config
from app.util.tools import app_path


class Module(Plugin):
    entry = 'github'
    brief_help = 'Github监听'
    manager: CommandDelegateManager = CommandDelegateManager.get_instance()

    @permission_required(level=Permission.GROUP_ADMIN)
    @manager.register(
        Alconna(
            headers=manager.headers,
            command=entry,
            options=[
                Subcommand('add', help_text='添加监听仓库', args=Args['repo': str, 'api': 'url'], options=[
                    Option('--branch|-b', args=Args['branch': str: '*'], help_text='指定监听的分支,使用 , 分隔, 默认监听全部分支')
                ]),
                Subcommand('modify', help_text='修改监听仓库配置', args=Args['repo': str], options=[
                    Option('--name|-n', args=Args['name': str], help_text='修改仓库名'),
                    Option('--api|-a', args=Args['api': 'url'], help_text='修改监听API'),
                    Option('--branch|-b', args=Args['branch': str: '*'], help_text='修改监听的分支, 使用 , 分隔, *: 监听所有分支')
                ]),
                Option('remove', help_text='删除监听仓库', args=Args['repo': str]),
                Option('list', help_text='列出当前群组所有监听仓库')
            ],
            help_text='Github监听, 仅管理可用'
        )
    )
    async def process(self, command: Arpamar, alc: Alconna):
        add = command.subcommands.get('add')
        modify = command.subcommands.get('modify')
        remove = command.options.get('remove')
        list_ = command.options.get('list')
        if all([not add, not modify, not remove, not list_]):
            return await self.print_help(alc.get_help())
        try:
            if add:
                branch = add['branch']['branch'].replace('，', ',').split(',') if 'branch' in add else ['*']
                group_id = str(self.group.id)
                if REPO.__contains__(group_id) and add['repo'] in REPO[group_id]:
                    return MessageChain.create([Plain('添加失败，该仓库名已存在!')])
                repo_info = {add['repo']: {'api': add['api'], 'branch': branch}}
                if await save_config('repo', group_id, repo_info, model='add'):
                    if not REPO.__contains__(group_id):
                        REPO.update({group_id: {}})
                    REPO[group_id].update(repo_info)
                    return MessageChain.create([Plain("添加成功!")])
            elif modify:
                group_id = str(self.group.id)
                repo = modify['repo']
                _name = modify.get('name')
                _api = modify.get('api')
                _branch = modify.get('branch')
                if all([not _name, not _api, not _branch]):
                    return self.args_error()
                if not REPO.__contains__(group_id) or repo not in REPO[group_id]:
                    return MessageChain.create([Plain('修改失败，该仓库名不存在!')])
                if _name:
                    _name = _name['name']
                    await save_config('repo', group_id, repo, model='remove')
                    await save_config('repo', group_id, {_name: REPO[group_id][repo]}, model='add')
                    REPO[group_id][_name] = REPO[group_id].pop(repo)
                    repo = _name
                if _api:
                    _api = _api['api']
                    REPO[group_id][repo]['api'] = _api
                    await save_config('repo', group_id, {repo: REPO[group_id][repo]}, model='add')
                if _branch:
                    _branch = _branch['branch']
                    REPO[group_id][repo]['branch'] = _branch.replace('，', ',').split(',')
                    await save_config('repo', group_id, {repo: REPO[group_id][repo]}, model='add')
                return MessageChain.create([Plain("修改成功!")])
            elif remove:
                group_id = str(self.group.id)
                if not REPO.__contains__(group_id) or remove['repo'] not in REPO[group_id]:
                    return MessageChain.create([Plain('删除失败，该仓库名不存在!')])
                await save_config('repo', group_id, remove['repo'], model='remove')
                REPO[group_id].pop(remove['repo'])
                return MessageChain.create([Plain("删除成功！")])
            elif list_:
                if REPO.get(str(self.group.id), 0):
                    return MessageChain.create(
                        '\r\n'.join(
                            f"{name}: \r\napi: {info['api']}\r\nbranch: {info['branch']}"
                            for name, info in REPO[str(self.group.id)].items()
                        )
                    )
                return MessageChain.create('该群组未配置Github监听仓库！')
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()


class Tasker(Scheduler):
    config = Config()
    cron = config.REPO_TIME

    async def process(self):
        if not self.config.ONLINE:  # 非 ONLINE 模式不监听仓库
            return
        if not self.config.REPO_ENABLE:  # 未开启仓库监听
            return
        logger.info('github_listener is running...')

        Path('./app/tmp/github').mkdir(parents=True, exist_ok=True)
        for group in REPO.keys():
            if os.path.exists(file := os.sep.join([app_path(), 'tmp', 'github', f'{group}.dat'])):
                with open(file, 'rb') as f:
                    obj = pickle.load(f)
            else:
                obj = {}
            for name, info in REPO[group].items():
                if not obj.__contains__(name):
                    obj.update({name: {}})
                try:
                    branches = await do_http_request(info['api'], 'get', 'JSON')
                    for branch in branches:
                        if info['branch'][0] != '*' and branch['name'] not in info['branch']:
                            continue
                        if not obj[name].__contains__(branch['name']):
                            obj[name].update({branch['name']: None})
                        if branch['commit']['sha'] != obj[name][branch['name']]:
                            obj[name][branch['name']] = branch['commit']['sha']
                            await message_push(self.app, group, name, branch)
                except aiohttp.client.ClientConnectorError:
                    logger.warning(f"获取仓库信息超时 - {info['api']}")
                except Exception as e:
                    logger.exception(f'获取仓库信息失败 - {e}')
            with open(file, 'wb') as f:
                pickle.dump(obj, f)


async def message_push(app, group, repo, branch):
    commit_info = requests.get(branch['commit']['url']).json()
    commit_time = datetime.strftime(
        datetime.strptime(commit_info['commit']['author']['date'],
                          "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8), '%Y-%m-%d %H:%M:%S')
    with enter_context(app=app):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('Recent Commits to ' + repo + ':' + branch['name']),
            Plain("\r\nCommit: " + commit_info['commit']['message']),
            Plain("\r\nAuthor: " + commit_info['commit']['author']['name']),
            Plain("\r\nUpdated: " + commit_time),
            Plain("\r\nLink: " + commit_info['html_url'])
        ]))
