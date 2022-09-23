import pickle
from datetime import datetime, timedelta
from typing import Union

import aiohttp.client
import requests
from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.model import Friend, Group, Member
from graia.scheduler import GraiaScheduler, timers
from loguru import logger

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.core.settings import REPO
from app.util.control import Permission
from app.util.network import general_request
from app.util.online_config import save_config
from app.util.phrases import *
from app.util.tools import app_path

core: AppCore = AppCore()
app = core.get_app()
sche: GraiaScheduler = core.get_scheduler()
manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry='github',
    brief_help='Github监听',
    alc=Alconna(
        headers=manager.headers,
        command='github',
        options=[
            Subcommand('add', help_text='添加监听仓库', args=Args['repo', str]['api', str, 'project/repo'], options=[
                Option('--branch|-b', args=Args['branch', str, '*'], help_text='指定监听的分支,使用 , 分隔, 默认监听全部分支')
            ]),
            Subcommand('modify', help_text='修改监听仓库配置', args=Args['repo', str], options=[
                Option('--name|-n', args=Args['name', str], help_text='修改仓库名'),
                Option('--api|-a', args=Args['api', str, 'project/repo'], help_text='修改监听API'),
                Option('--branch|-b', args=Args['branch', str, '*'], help_text='修改监听的分支, 使用 , 分隔, *: 监听所有分支')
            ]),
            Option('remove', help_text='删除监听仓库', args=Args['repo', str]),
            Option('list', help_text='列出当前群组所有监听仓库')
        ],
        help_text='Github监听, 仅管理可用'
    )
)
@Permission.require(level=Permission.GROUP_ADMIN)
async def process(sender: Union[Friend, Group], command: Arpamar, alc: Alconna, _: Union[Friend, Member]):
    add = command.subcommands.get('add')
    modify = command.subcommands.get('modify')
    remove = command.options.get('remove')
    list_ = command.options.get('list')
    if all([not add, not modify, not remove, not list_]):
        return await print_help(alc.get_help())
    if not isinstance(sender, Group):
        return MessageChain('请在群聊中使用')
    try:
        if add:
            branch = add['branch']['branch'].replace('，', ',').split(',') if 'branch' in add else ['*']
            group_id = str(sender.id)
            if REPO.__contains__(group_id) and add['repo'] in REPO[group_id]:
                return MessageChain([Plain('添加失败，该仓库名已存在!')])
            if add['api'] == 'project/repo':
                return MessageChain([Plain('添加失败，监听仓库不能为空!')])
            repo_info = {
                add['repo']: {
                    'api': f"https://api.github.com/repos/{add['api'].strip('/')}/branches",
                    'branch': branch
                }
            }
            await save_config('repo', sender, repo_info, model='add')
            if group_id not in REPO:
                REPO[group_id] = repo_info
            else:
                REPO[group_id].update(repo_info)
            return MessageChain([Plain("添加成功!")])
        elif modify:
            group_id = str(sender.id)
            repo = modify['repo']
            _name = modify.get('name')
            _api = modify.get('api')
            _branch = modify.get('branch')
            if all([not _name, not _api, not _branch]):
                return args_error()
            if not REPO.__contains__(group_id) or repo not in REPO[group_id]:
                return MessageChain([Plain('修改失败，该仓库名不存在!')])
            if _name:
                _name = _name['name']
                await save_config('repo', sender, repo, model='remove')
                await save_config('repo', sender, {_name: REPO[group_id][repo]}, model='add')
                REPO[group_id][_name] = REPO[group_id].pop(repo)
                repo = _name
            if _api:
                if _api['api'] == 'project/repo':
                    return MessageChain([Plain('修改失败，监听仓库不能为空!')])
                _api = f"https://api.github.com/repos/{_api['api'].strip('/')}/branches"
                REPO[group_id][repo]['api'] = _api
                await save_config('repo', sender, {repo: REPO[group_id][repo]}, model='add')
            if _branch:
                _branch = _branch['branch']
                REPO[group_id][repo]['branch'] = _branch.replace('，', ',').split(',')
                await save_config('repo', sender, {repo: REPO[group_id][repo]}, model='add')
            return MessageChain([Plain("修改成功!")])
        elif remove:
            group_id = str(sender.id)
            if not REPO.__contains__(group_id) or remove['repo'] not in REPO[group_id]:
                return MessageChain([Plain('删除失败，该仓库名不存在!')])
            await save_config('repo', sender, remove['repo'], model='remove')
            REPO[group_id].pop(remove['repo'])
            return MessageChain([Plain("删除成功！")])
        elif list_:
            if REPO.get(str(sender.id), 0):
                return MessageChain(
                    '\r\n'.join(
                        f"{name}: \r\napi: {info['api']}\r\nbranch: {info['branch']}"
                        for name, info in REPO[str(sender.id)].items()
                    )
                )
            return MessageChain('该群组未配置Github监听仓库！')
        return args_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()


@sche.schedule(timers.crontabify(config.REPO_TIME))
@logger.catch
async def tasker():
    if not config.ONLINE:  # 非 ONLINE 模式不监听仓库
        return
    if not config.REPO_ENABLE:  # 未开启仓库监听
        return
    logger.info('github_listener is running...')

    app_path().joinpath('tmp/github').mkdir(parents=True, exist_ok=True)
    for group in REPO.keys():
        file = app_path().joinpath(f'tmp/github/{group}.dat')
        if file.exists():
            with open(file, 'rb') as f:
                obj = pickle.load(f)
        else:
            obj = {}
        for name, info in REPO[group].items():
            if not obj.__contains__(name):
                obj.update({name: {}})
            try:
                branches = await general_request(info['api'], 'get', 'JSON')
                for branch in branches:
                    if info['branch'][0] != '*' and branch['name'] not in info['branch']:
                        continue
                    if not obj[name].__contains__(branch['name']):
                        obj[name].update({branch['name']: None})
                    if branch['commit']['sha'] != obj[name][branch['name']]:
                        obj[name][branch['name']] = branch['commit']['sha']
                        await message_push(group, name, branch)
            except aiohttp.client.ClientConnectorError:
                logger.warning(f"获取仓库信息超时 - {info['api']}")
            except Exception as e:
                logger.exception(f'获取仓库信息失败 - {e}')
        with open(file, 'wb') as f:
            pickle.dump(obj, f)


async def message_push(group, repo, branch):
    commit_info = requests.get(branch['commit']['url']).json()
    commit_time = datetime.strftime(
        datetime.strptime(commit_info['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8),
        '%Y-%m-%d %H:%M:%S'
    )
    await app.send_group_message(
        group,
        MessageChain(
            [
                Plain(f'Recent Commits to {repo}:' + branch['name']),
                Plain("\r\nCommit: " + commit_info['commit']['message']),
                Plain(
                    "\r\nAuthor: " + commit_info['commit']['author']['name']
                ),
                Plain("\r\nUpdated: " + commit_time),
                Plain("\r\nLink: " + commit_info['html_url']),
            ]
        ),
    )
