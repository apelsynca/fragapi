from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.applications import Starlette

from src.app import app as frag_app
from src.auth.dependencies import _auth_subject_factory_cache
from src.fragment_rest.dependecies import get_fragment_rest
from src.fragment_rest.main import FragmentRest
from src.postgres import get_db_session
from tests.fixtures.auth import AuthSubjectFixture


@pytest_asyncio.fixture
async def app(
    auth_subject: AuthSubjectFixture, session: AsyncSession, fragment_rest: FragmentRest
) -> AsyncGenerator[Starlette]:
    frag_app.dependency_overrides[get_db_session] = lambda: session
    frag_app.dependency_overrides[get_fragment_rest] = lambda: fragment_rest

    for auth_subject_getter in _auth_subject_factory_cache.values():
        frag_app.dependency_overrides[auth_subject_getter] = lambda: auth_subject

    yield frag_app

    frag_app.dependency_overrides.pop(get_db_session)


@pytest_asyncio.fixture
async def client(app: Starlette) -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
