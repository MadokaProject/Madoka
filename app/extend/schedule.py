import os

from graia import scheduler
from graia.scheduler import timers

from app.core.config import *
from app.core.settings import LISTEN_MC_SERVER
from app.extend.NetEaseCloudMusicAction import NetEase_action
from app.extend.github import github_listener
from app.extend.mc import mc_listener
from app.util.tools import app_path


async def custom_schedule(loop, bcc, bot):
    sche = scheduler.GraiaScheduler(loop=loop, broadcast=bcc)

    if not os.path.exists(path := os.sep.join([app_path(), 'tmp', 'mcserver'])):
        os.makedirs(path)
    for ips, qq, delay in LISTEN_MC_SERVER:
        @sche.schedule(timers.every_custom_seconds(delay))
        async def mc_listen_schedule():
            await mc_listener(bot, path, ips, qq, delay)

    @sche.schedule(timers.crontabify("0 8 * * *"))
    async def NetEase_actions():
        await NetEase_action(bot)

    @sche.schedule(timers.crontabify(REPO_TIME))
    async def github_commit_listener():
        await github_listener(bot)