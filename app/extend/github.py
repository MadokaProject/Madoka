import asyncio
import requests
from app.util import mysql

from graia.application import enter_context, MessageChain
from graia.application.message.elements.internal import Plain

from datetime import datetime, timedelta
from app.core.config import *


async def github_listener(app):
    while True:
        await asyncio.sleep(REPO_TIME * 60)  # 间隔时间
        app.logger.info('github_listener is running...')

        group = REPO_GROUP
        repo = REPO_NAME  # 仓库名
        repo_api = REPO_API  # 仓库api
        for repo_num in range(len(repo)):
            if mysql.find_table(repo[repo_num]) == 0:  # 若数据表不存在
                mysql.github_create(repo[repo_num])  # 创建数据表
            branches = requests.get(repo_api[repo_num]).json()  # 获取该仓库的全部branch json
            commit = mysql.github_find(repo[repo_num])  # 查找该仓库全部已有提交信息
            b = [i[1] for i in commit]
            for branch in branches:  # 挨个分支进行检测
                if branch['name'] in b:  # 若branch已存在
                    if commit[b.index(branch['name'])][2] != branch['commit']['sha']:  # sha值不一致，更新数据表信息，发送群消息通知
                        mysql.github_update(repo[repo_num], branch['name'], branch['commit']['sha'])  # 更新数据表
                        await message_push(app, group, branch)  # 推送消息
                else:  # 若数据表中无对应branch，插入信息至数据表，发送群消息
                    mysql.github_insert(repo[repo_num], branch['name'], branch['commit']['sha'])
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
