import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import requests
from graia.ariadne.context import enter_context
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from loguru import logger

from app.api.doHttp import doHttpRequest
from app.core.config import Config
from app.core.settings import REPO
from app.util.tools import app_path


async def github_listener(app):
    config = Config()
    if not config.ONLINE:  # 非 ONLINE 模式不监听仓库
        return
    if not config.REPO_ENABLE:  # 未开启仓库监听
        return
    logger.info('github_listener is running...')

    Path('./app/tmp/github').mkdir(parents=True, exist_ok=True)
    for group in REPO.keys():
        if os.path.exists(file := os.sep.join([app_path(), 'tmp', 'github', f'{group}.dat'])):
            with open(file, 'rb') as f:
                obj = pickle.load(f)
        else:
            obj = {}
        for name, api in REPO[group].items():
            if not obj.__contains__(name):
                obj.update({name: {}})
            branches = await doHttpRequest(api, 'get', 'JSON')
            for branch in branches:
                if not obj[name].__contains__(branch['name']):
                    obj[name].update({branch['name']: None})
                if branch['commit']['sha'] != obj[name][branch['name']]:
                    obj[name][branch['name']] = branch['commit']['sha']
                    await message_push(app, group, name, branch)
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
