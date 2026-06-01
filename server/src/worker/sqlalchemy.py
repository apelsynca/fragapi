from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from taskiq import Context, TaskiqDepends, TaskiqEvents, TaskiqState

from src.kit.database.postgres import AsyncSessionMaker as AsyncSessionMakerType
from src.kit.database.postgres import create_async_sessionmaker
from src.logging import Logger
from src.postgres import AsyncSession, create_async_engine
from src.worker import broker

log: Logger = structlog.get_logger()


def _get_worker_pool_name() -> str:
    return "worker"


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def initialize_engine(state: TaskiqState) -> None:
    pool_name = _get_worker_pool_name()
    _sqlalchemy_engine = create_async_engine("worker", pool_logging_name=pool_name)
    state.async_sessionmaker = create_async_sessionmaker(_sqlalchemy_engine)

    log.info("Created SQLAlchemy engine", pool_name=pool_name)


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def dispose_engine(state: TaskiqState) -> None:
    if state.async_sessionmaker is not None:
        await state.async_sessionmaker.dispose()
        log.info("Disposed SQLAlchemy engine")
        state.async_sessionmaker = None


async def get_db_session(
    context: Annotated[Context, TaskiqDepends()],
) -> AsyncGenerator[AsyncSession]:
    try:
        sessionmaker: AsyncSessionMakerType = context.state.async_sessionmaker
    except AttributeError as e:
        raise RuntimeError(
            "Session is not preset in the context state. "
            "Did you (re)moved broker events?"
        ) from e

    async with sessionmaker() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        else:
            await session.commit()


WorkerAsyncSessionDependency = Annotated[AsyncSession, TaskiqDepends(get_db_session)]
