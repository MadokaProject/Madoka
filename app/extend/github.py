from datetime import datetime, timedelta

import requests
from graia.application import enter_context, MessageChain
from graia.application.message.elements.internal import Plain

from app.core.config import Config
from app.core.settings import *
from app.util.dao import MysqlDao


async def github_listener(app):
    config = Config()
    if not config.REPO_ENABLE:  # 未开启仓库监听
        return
    app.logger.info('github_listener is running...')

    group = config.REPO_GROUP
    repo = [i for i in REPO.keys()]
    repo_api = [i for i in REPO.values()]
    if not repo or not repo_api:
        return
    for repo_num in range(len(repo)):
        branches = requests.get(repo_api[repo_num]).json()  # 获取该仓库的全部branch json
        for branch in branches:  # 挨个分支进行检测
            with MysqlDao() as db:
                res = db.query(
                    'SELECT * FROM github where repo=%s and branch=%s',
                    [repo[repo_num], branch['name']]
                )
                if res:
                    if res[0][3] != branch['commit']['sha']:  # sha不一致
                        db.update(
                            'update github set sha = %s where repo=%s and branch=%s',
                            [[branch['commit']['sha']], repo[repo_num], branch['name']]
                        )
                        await message_push(app, group, repo[repo_num], branch)
                else:
                    db.update(
                        'INSERT INTO github(repo, branch, sha) VALUES(%s, %s, %s)',
                        [repo[repo_num], branch['name'], branch['commit']['sha']]
                    )
                    await message_push(app, group, repo[repo_num], branch)


async def message_push(app, groups, repo, branch):
    commit_info = requests.get(branch['commit']['url']).json()
    commit_time = datetime.strftime(
        datetime.strptime(commit_info['commit']['author']['date'],
                          "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8), '%Y-%m-%d %H:%M:%S')
    with enter_context(app=app):
        for group in groups:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('Recent Commits to ' + repo + ':' + branch['name']),
                Plain("\r\nCommit: " + commit_info['commit']['message']),
                Plain("\r\nAuthor: " + commit_info['commit']['author']['name']),
                Plain("\r\nUpdated: " + commit_time),
                Plain("\r\nLink: " + commit_info['html_url'])
            ]))
