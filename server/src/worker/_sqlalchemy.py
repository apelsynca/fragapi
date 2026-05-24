import contextlib
from collections.abc import AsyncGenerator

import structlog
from taskiq import TaskiqMiddleware

from src.kit.database.postgres import AsyncSessionMaker as AsyncSessionMakerType
from src.kit.database.postgres import create_async_sessionmaker
from src.logging import Logger
from src.postgres import AsyncEngine, AsyncSession, create_async_engine

log: Logger = structlog.get_logger()

_sqlalchemy_engine: AsyncEngine | None = None
_sqlalchemy_async_sessionmaker: AsyncSessionMakerType | None = None


async def dispose_sqlalchemy_engine() -> None:
    global _sqlalchemy_engine
    if _sqlalchemy_engine is not None:
        await _sqlalchemy_engine.dispose()
        log.info("Disposed SQLAlchemy engine")
        _sqlalchemy_engine = None


def _get_worker_pool_name() -> str:
    return "worker"


class SQLAlchemyMiddleware(TaskiqMiddleware):
    @classmethod
    def get_async_session(cls) -> contextlib.AbstractAsyncContextManager[AsyncSession]:
        global _sqlalchemy_async_sessionmaker
        if _sqlalchemy_async_sessionmaker is None:
            raise RuntimeError("SQLAlchemy not initialized")
        return _sqlalchemy_async_sessionmaker()

    async def startup(self) -> None:
        global _sqlalchemy_engine, _sqlalchemy_async_sessionmaker
        pool_name = _get_worker_pool_name()
        _sqlalchemy_engine = create_async_engine("worker", pool_logging_name=pool_name)
        _sqlalchemy_async_sessionmaker = create_async_sessionmaker(_sqlalchemy_engine)

        log.info("Created database engine", pool_name=pool_name)

    async def shutdown(self) -> None:
        await dispose_sqlalchemy_engine()


@contextlib.asynccontextmanager
async def AsyncSessionMaker() -> AsyncGenerator[AsyncSession]:
    async with SQLAlchemyMiddleware.get_async_session() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        else:
            await session.commit()
