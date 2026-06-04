from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from src.auth.service import auth as auth_service
from src.worker import broker
from src.worker.sqlalchemy import get_db_session


@broker.task(task_name="auth.delete_expired", schedule=[{"cron": "0 0 * * *"}])
async def auth_delete_expired(
    session: Annotated[AsyncSession, TaskiqDepends(get_db_session)],
) -> None:
    await auth_service.delete_expired(session)
