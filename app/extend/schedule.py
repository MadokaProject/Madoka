from graia.ariadne.app import Ariadne
from graia.scheduler import GraiaScheduler, timers
from loguru import logger

from app.core.config import Config
from app.core.settings import LISTEN_MC_SERVER
from app.extend.mc import mc_listener
from app.util.tools import app_path
from app.util.version import check_version


async def custom_schedule(scheduler: GraiaScheduler, bot: Ariadne):
    config = Config()
    path = app_path().joinpath('tmp/mcserver')
    path.mkdir(parents=True, exist_ok=True)
    for ips, qq, delay in LISTEN_MC_SERVER:
        @scheduler.schedule(timers.every_custom_seconds(delay))
        async def mc_listen_schedule():
            await mc_listener(bot, path, ips, qq, delay)

    @scheduler.schedule(timers.every_custom_hours(24))
    @logger.catch
    async def version_info_listener():
        await check_version(bot, config)

#
# async def TaskerProcess(scheduler: GraiaScheduler, obj):
#     @scheduler.schedule(timers.crontabify(obj.cron))
#     @logger.catch
#     async def process():
#         await obj.process()
