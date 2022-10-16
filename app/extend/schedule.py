from graia.ariadne import Ariadne
from graia.scheduler import GraiaScheduler, timers
from loguru import logger

from app.core.app import AppCore
from app.util.version import check_version

core: AppCore = AppCore()
app: Ariadne = core.get_app()
sche: GraiaScheduler = core.get_scheduler()


@sche.schedule(timers.crontabify("0 6 * * * 0"))
@logger.catch
async def version_info_listener():
    await check_version()
