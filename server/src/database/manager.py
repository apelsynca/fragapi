from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from src.config import settings
from src.database.postgres import create_engine
from src.kit.models import Model


class SessionManager:
    def __init__(
        self,
        engine: AsyncEngine | None = None,
        session_maker: async_sessionmaker[AsyncSession] | None = None,
    ):
        self._engine = engine
        self._session_maker = session_maker

    @classmethod
    def from_url(cls, url: str):
        _instance = cls()
        _instance.feed_url(url)

        return _instance

    def feed_url(self, url: str) -> None:
        self._engine = create_engine(url)
        self._session_maker = async_sessionmaker(
            bind=self._engine, autocommit=False, expire_on_commit=False
        )

    async def close(self):
        if self._engine is None:
            raise RuntimeError(f"{self.__class__.__name__} engine is not set")

        await self._engine.dispose()
        self._engine = None
        self._session_maker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise RuntimeError(f"{self.__class__.__name__} engine is not set")

        async with self._engine.begin() as conn:
            try:
                yield conn
            except:
                await conn.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise RuntimeError(f"{self.__class__.__name__} session_maker is not set")

        session = self._session_maker()

        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_all(self, conn: AsyncConnection):
        await conn.run_sync(Model.metadata.create_all)

    async def drop_all(self, conn: AsyncConnection):
        await conn.run_sync(Model.metadata.drop_all)


session_manager = SessionManager.from_url(url=settings.database_url.get_secret_value())
