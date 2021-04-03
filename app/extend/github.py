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

        repo = REPO_NAME  # 仓库名
        repo_api = REPO_API  # 仓库api
        for repo_num in range(len(repo)):
            if mysql.find_table(repo[repo_num]) == 0:  # 若数据表不存在
                mysql.github_create(repo[repo_num])  # 创建数据表
            branches = requests.get(repo_api[repo_num]).json()  # 获取该仓库的全部branch json
            commit = mysql.github_find(repo[repo_num])  # 查找该仓库全部已有提交信息
            for branch in branches:  # 挨个分支进行检测
                for i in commit:
                    if i[1] == branch['name']:  # 若数据表已存在对应branch
                        if i[2] == branch['commit']['sha']:  # sha值相同，不做处理
                            return
                        else:  # sha值不一致，更新数据表信息，发送群消息通知
                            mysql.github_update(repo[repo_num], branch['name'], branch['commit']['sha'])  # 更新数据表
                            commit_info = requests.get(branch['commit']['url']).json()
                            commit_time = datetime.strftime(
                                datetime.strptime(commit_info['commit']['author']['date'],
                                                  "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8), '%Y-%m-%d %H:%M:%S')
                            with enter_context(app=app):
                                await app.sendGroupMessage(1146399464, MessageChain.create([
                                    Plain("commit: " + commit_info['commit']['message']),
                                    Plain("\nname: " + commit_info['commit']['author']['name']),
                                    Plain("\ntime: " + commit_time),
                                    Plain("\nurl: " + commit_info['html_url'])
                                ]))
                            return
                else:  # 若数据表中无对应branch，插入信息至数据表，发送群消息
                    mysql.github_insert(repo[repo_num], branch['name'], branch['commit']['sha'])
                    commit_info = requests.get(branch['commit']['url']).json()
                    commit_time = datetime.strftime(
                        datetime.strptime(commit_info['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(
                            hours=8), '%Y-%m-%d %H:%M:%S')
                    with enter_context(app=app):
                        await app.sendGroupMessage(1146399464, MessageChain.create([
                            Plain("commit: " + commit_info['commit']['message']),
                            Plain("\nname: " + commit_info['commit']['author']['name']),
                            Plain("\ntime: " + commit_time),
                            Plain("\nurl: " + commit_info['html_url'])
                        ]))
