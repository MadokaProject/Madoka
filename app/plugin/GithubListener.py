import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp.client
import requests
from graia.ariadne.context import enter_context
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.api.doHttp import doHttpRequest
from app.core.config import Config
from app.core.settings import REPO
from app.plugin.base import Plugin, Scheduler
from app.util.control import Permission
from app.util.decorator import permission_required
from app.util.onlineConfig import save_config
from app.util.tools import app_path
from app.util.tools import isstartswith


class Module(Plugin):
    entry = ['.github']
    brief_help = '\r\n[√]\tGithub监听: github'
    full_help = \
        '.github\t仅管理可用\r\n' \
        '.github add [repo_name] [repo_api] [branch(可选)]\t添加监听仓库，可指定监听的分支（,分隔）\r\n' \
        '.github modify [repo_name] [name|api|branch] [value]\t修改监听仓库配置\r\n' \
        '.github remove [repo_name]\t删除监听仓库\r\n' \
        '.github list\t列出所有监听仓库\r\n' \
        'branch参数可为：\r\n*：监听所有分支\r\n' \
        '分支名：指定监听的分支，用“,”分隔'

    @permission_required(level=Permission.GROUP_ADMIN)
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], 'add'):
                assert len(self.msg) >= 3
                group_id = str(self.group.id)
                if REPO.__contains__(group_id) and self.msg[1] in REPO[group_id]:
                    self.resp = MessageChain.create([Plain('添加失败，该仓库名已存在！')])
                    return
                repo_info = {self.msg[1]: {'api': self.msg[2],
                                           'branch': self.msg[3].replace('，', ',').split(',') if len(
                                               self.msg) == 4 else ['*']}}
                if await save_config('repo', group_id, repo_info, model='add'):
                    self.resp = MessageChain.create([Plain("添加成功！")])
                    if not REPO.__contains__(group_id):
                        REPO.update({group_id: {}})
                    REPO[group_id].update(repo_info)
            elif isstartswith(self.msg[0], 'modify'):
                assert len(self.msg) == 4 and self.msg[2] in ['name', 'api', 'branch']
                group_id = str(self.group.id)
                if not REPO.__contains__(group_id) or self.msg[1] not in REPO[group_id]:
                    self.resp = MessageChain.create([Plain('修改失败，该仓库名不存在！')])
                    return
                if self.msg[2] == 'name':
                    await save_config('repo', group_id, self.msg[1], model='remove')
                    await save_config('repo', group_id, {self.msg[3]: REPO[group_id][self.msg[1]]}, model='add')
                    REPO[group_id][self.msg[3]] = REPO[group_id].pop(self.msg[1])
                else:
                    self.msg[3] = self.msg[3] if self.msg[2] == 'api' else self.msg[3].replace('，', ',').split(',')
                    await save_config('repo', group_id, {self.msg[1]: {self.msg[2]: self.msg[3]}}, model='add')
                    REPO[group_id][self.msg[1]][self.msg[2]] = self.msg[3]
                self.resp = MessageChain.create([Plain("修改成功！")])
            elif isstartswith(self.msg[0], 'remove'):
                assert len(self.msg) == 2
                group_id = str(self.group.id)
                if not REPO.__contains__(group_id) or self.msg[1] not in REPO[group_id]:
                    self.resp = MessageChain.create([Plain('删除失败，该仓库名不存在！')])
                    return
                await save_config('repo', group_id, self.msg[1], model='remove')
                REPO[group_id].pop(self.msg[1])
                self.resp = MessageChain.create([Plain("删除成功！")])
            elif isstartswith(self.msg[0], 'list'):
                self.resp = MessageChain.create([Plain(
                    '\r\n'.join([f'{name}: \r\napi: {api}\r\nbranch: {branch}' for name, api, branch in
                                 REPO[str(self.group.id)].items()]))])
            else:
                self.args_error()
                return
        except AssertionError:
            self.args_error()
        except Exception as e:
            logger.exception(e)
            self.unkown_error()


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
                    branches = await doHttpRequest(info['api'], 'get', 'JSON')
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
