import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Transaction
from tonutils.clients import ToncenterClient

from src.exceptions import BadRequest, ResourceNotFound
from src.ton_transaction.tasks import ton_transaction_find_real_hash
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction


@pytest.fixture(autouse=True)
def toncenter_mock(mocker: MockerFixture) -> MagicMock:
    client = MagicMock(spec=ToncenterClient)
    mocker.patch("src.ton_transaction.tasks.create_toncenter", return_value=client)
    return client


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


@pytest.mark.asyncio
async def test_lookup_paginates_past_first_100_transactions(
    save_fixture, session, toncenter_mock, mocker
):
    purchase = await create_ton_transaction(save_fixture, hash="external-hash")
    unrelated = MagicMock(spec=Transaction)
    unrelated.in_msg = MagicMock()
    unrelated.cell = MagicMock()
    unrelated.in_msg.is_external = True
    unrelated.lt = 123
    unrelated.now = int(purchase.created_at.timestamp())
    unrelated.cell.hash = b"first-page"
    matching = MagicMock(spec=Transaction)
    matching.in_msg = MagicMock()
    matching.cell = MagicMock()
    matching.in_msg.is_external = True
    matching.cell.hash = b"found"
    mocker.patch("src.ton_transaction.tasks.Cell.one_from_boc")
    mocker.patch(
        "src.ton_transaction.tasks.Transaction.deserialize",
        side_effect=[unrelated] * 100 + [matching],
    )
    mocker.patch(
        "src.ton_transaction.tasks.normalize_hash",
        side_effect=["different"] * 100 + ["external-hash"],
    )
    toncenter_mock.provider = MagicMock()
    toncenter_mock.provider.get_transactions = AsyncMock(
        side_effect=[
            MagicMock(result=[MagicMock(data="boc")] * 100),
            MagicMock(result=[MagicMock(data="boc")]),
        ]
    )
    await ton_transaction_find_real_hash(
        ton_transaction_id=purchase.id, session=session
    )
    assert purchase.hash == b"found".hex()
    assert toncenter_mock.provider.get_transactions.await_count == 2
    second_call = toncenter_mock.provider.get_transactions.await_args_list[1]
    assert second_call.kwargs["lt"] == 123
    assert second_call.kwargs["from_hash"] == b"first-page".hex()
