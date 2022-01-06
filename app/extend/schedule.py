import os

from graia import scheduler
from graia.scheduler import timers
from loguru import logger

from app.core.config import Config
from app.core.settings import LISTEN_MC_SERVER
from app.extend.mc import mc_listener
from app.util.version import check_version
from app.util.tools import app_path


async def custom_schedule(loop, bcc, bot):
    sche = scheduler.GraiaScheduler(loop=loop, broadcast=bcc)
    config = Config()

    if not os.path.exists(path := os.sep.join([app_path(), 'tmp', 'mcserver'])):
        os.makedirs(path)
    for ips, qq, delay in LISTEN_MC_SERVER:
        @sche.schedule(timers.every_custom_seconds(delay))
        async def mc_listen_schedule():
            await mc_listener(bot, path, ips, qq, delay)

    @sche.schedule(timers.every_custom_hours(24))
    @logger.catch
    async def version_info_listener():
        await check_version(bot, config)


async def TaskerProcess(loop, bcc, obj):
    sche = scheduler.GraiaScheduler(loop=loop, broadcast=bcc)

    @sche.schedule(timers.crontabify(obj.cron))
    @logger.catch
    async def process():
        await obj.process()
