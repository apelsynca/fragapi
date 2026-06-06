from typing import Annotated

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from src.auth.service import auth as auth_service
from src.worker import broker
from src.worker.sqlalchemy import get_db_session

log = structlog.get_logger()


# task_name="auth.delete_expired",
@broker.task(schedule=[{"cron": "0 0 * * *"}], task_name="auth_delete_expired")
async def auth_delete_expired(
    session: Annotated[AsyncSession, TaskiqDepends(get_db_session)],
) -> None:
    await auth_service.delete_expired(session)


#
# # task_name="auth.pissie_piss",
# # without name
# @broker.task(schedule=[{"interval": 3}])
# async def auth_pissie_piss() -> None:
#     log.info("Aswell as info INTERVAL 3")
#     print("Scheduled at interval 3 pissie piss", utc_now().strftime(""))
#
#
# @broker.task(schedule=[{"cron": "* * * * *"}])
# async def some_task_every_minute() -> None:
#     print("At cron")
#     log.info("Aswell as info CRON")
