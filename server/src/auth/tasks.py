from datetime import timedelta
from typing import Annotated

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from src.auth.service import auth as auth_service
from src.kit.utils import utc_now
from src.worker import broker
from src.worker.sqlalchemy import get_db_session

log = structlog.get_logger()


@broker.task(task_name="auth.delete_expired", schedule=[{"cron": "0 0 * * *"}])
async def auth_delete_expired(
    session: Annotated[AsyncSession, TaskiqDepends(get_db_session)],
) -> None:
    await auth_service.delete_expired(session)


@broker.task(
    task_name="auth.pissie_piss", schedule=[{"interval": timedelta(seconds=5)}]
)
async def auth_pissie_piss() -> None:
    log.info("Aswell as info")
    print("This is from scheduled bs but pissie", utc_now().strftime(""))
