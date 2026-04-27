from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.applications import Starlette

from src.app import app as rolls_app
from src.postgres import get_db_session


@pytest_asyncio.fixture
async def app(session: AsyncSession) -> AsyncGenerator[Starlette]:
    rolls_app.dependency_overrides[get_db_session] = lambda: session

    yield rolls_app

    rolls_app.dependency_overrides.pop(get_db_session)


@pytest_asyncio.fixture
async def client(app: Starlette) -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
