import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from tonutils.clients import ToncenterClient

from src.exceptions import BadRequest, ResourceNotFound
from src.ton_transaction.tasks import ton_transaction_find_real_hash
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction


@pytest.fixture(autouse=True)
def toncenter_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.ton_transaction.tasks.toncenter_client", spec=ToncenterClient
    )


# TODO: remove that in favor of retry or smth
@pytest.fixture(autouse=True)
def asyncio_sleep_mock(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("src.ton_transaction.tasks.asyncio.sleep", new=AsyncMock())


@pytest.mark.asyncio
async def test_find_real_hash_raises_if_ton_transaction_is_not_found_by_id(
    session: AsyncSession,
) -> None:
    with pytest.raises(ResourceNotFound):
        await ton_transaction_find_real_hash(
            ton_transaction_id=uuid.uuid4(), session=session
        )


@pytest.mark.asyncio
async def test_find_real_hash_raises_if_ton_transaction_without_hash(
    save_fixture: SaveFixture, session: AsyncSession
) -> None:
    ton_transaction = await create_ton_transaction(save_fixture, hash=None)

    with pytest.raises(BadRequest):
        await ton_transaction_find_real_hash(
            ton_transaction_id=ton_transaction.id, session=session
        )
