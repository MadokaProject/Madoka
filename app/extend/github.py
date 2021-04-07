from datetime import datetime, timedelta

import requests
from graia.application import enter_context, MessageChain
from graia.application.message.elements.internal import Plain

from app.core.config import *
from app.util.dao import MysqlDao


async def github_listener(app):
    app.logger.info('github_listener is running...')

    group = REPO_GROUP
    repo = REPO_NAME  # 仓库名
    repo_api = REPO_API  # 仓库api
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
                        await message_push(app, group, branch)
                else:
                    db.update(
                        'INSERT INTO github(repo, branch, sha) VALUES(%s, %s, %s)',
                        [repo[repo_num], branch['name'], branch['commit']['sha']]
                    )
                    await message_push(app, group, branch)


async def message_push(app, groups, branch):
    commit_info = requests.get(branch['commit']['url']).json()
    commit_time = datetime.strftime(
        datetime.strptime(commit_info['commit']['author']['date'],
                          "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8), '%Y-%m-%d %H:%M:%S')
    with enter_context(app=app):
        for group in groups:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(branch['name']),
                Plain("\r\ncommit: " + commit_info['commit']['message']),
                Plain("\r\nname: " + commit_info['commit']['author']['name']),
                Plain("\r\ntime: " + commit_time),
                Plain("\r\nurl: " + commit_info['html_url'])
            ]))
