from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.applications import Starlette

from src.app import app as frag_app
from src.auth.dependencies import _auth_subject_factory_cache
from src.integrations.fragment import get_fragment
from src.postgres import get_db_session
from src.redis import Redis, get_redis
from tests.fixtures.auth import AuthSubjectFixture


class IsolatedSessionTestClient(httpx.AsyncClient):
    """
    Test client that mimics production behavior by clearing session before requests.

    In production, each HTTP request gets a fresh database session. This client
    simulates that by expunging all objects from the test session before each
    request, catching lazy='raise' errors that would otherwise pass in tests.

    Disable for specific tests with @pytest.mark.keep_session_state marker.
    """

    def __init__(
        self, session: AsyncSession, auto_expunge: bool, *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self._session = session
        self._auto_expunge = auto_expunge

    async def request(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Expunge session before each request to simulate production."""
        if self._auto_expunge:
            self._session.expunge_all()
        return await super().request(*args, **kwargs)


@pytest_asyncio.fixture
async def app(
    auth_subject: AuthSubjectFixture,
    session: AsyncSession,
    fragment: MagicMock,
    redis: Redis,
) -> AsyncGenerator[Starlette]:
    frag_app.dependency_overrides[get_db_session] = lambda: session
    frag_app.dependency_overrides[get_fragment] = lambda: fragment
    frag_app.dependency_overrides[get_redis] = lambda: redis

    for auth_subject_getter in _auth_subject_factory_cache.values():
        frag_app.dependency_overrides[auth_subject_getter] = lambda: auth_subject

    yield frag_app

    frag_app.dependency_overrides.pop(get_db_session)


@pytest_asyncio.fixture
async def client(
    app: Starlette, session: AsyncSession
) -> AsyncGenerator[httpx.AsyncClient]:
    async with IsolatedSessionTestClient(
        session=session,
        auto_expunge=True,
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
