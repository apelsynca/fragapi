import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.worker._sqlalchemy import SQLAlchemyMiddleware


@pytest.fixture(autouse=True)
def patch_middlewares(mocker: MockerFixture, session: AsyncSession) -> None:
    mocker.patch.object(SQLAlchemyMiddleware, "get_async_session", return_value=session)
