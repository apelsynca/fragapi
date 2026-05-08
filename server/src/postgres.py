from collections.abc import AsyncGenerator
from typing import Literal

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from src.config import settings
from src.kit.database.postgres import (
    AsyncEngine,
    AsyncSession,
    AsyncSessionMaker,
)
from src.kit.database.postgres import create_async_engine as _create_async_engine

type ProcessName = Literal["app", "bot", "script"]


def create_async_engine(
    process_name: ProcessName, *, pool_logging_name: str | None = None
) -> AsyncEngine:
    return _create_async_engine(
        dsn=str(settings.get_postgres_dsn("asyncpg")),
        application_name=f"{settings.ENV.value}.{process_name}",
        pool_logging_name=pool_logging_name or process_name,
        pool_size=settings.DATABASE_POOL_SIZE,
        pool_recycle=settings.DATABASE_POOL_RECYCLE_SECONDS,
        command_timeout=settings.DATABASE_COMMAND_TIMEOUT_SECONDS,
    )


class AsyncSessionMiddleware:
    """Middleware to put async_session into state on every request"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            return await self.app(scope, receive, send)

        sessionmaker: AsyncSessionMaker = scope["state"]["async_sessionmaker"]
        async with sessionmaker() as session:
            scope["state"]["async_session"] = session
            await self.app(scope, receive, send)


async def get_db_sessionmaker(request: Request) -> AsyncSessionMaker:
    return request.state.async_sessionmaker


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    try:
        session = request.state.async_session
    except AttributeError as e:
        raise RuntimeError(
            "Session is not present in the request state. "
            "Did you forget to add AsyncSessionMiddleware?"
        ) from e

    try:
        yield session
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


__all__ = [
    "AsyncEngine",
    "AsyncSession",
    "AsyncSessionMiddleware",
    "create_async_engine",
    "get_db_session",
    "get_db_sessionmaker",
]
