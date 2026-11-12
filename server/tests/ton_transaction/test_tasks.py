import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Transaction
from tonutils.clients import ToncenterClient

from src.exceptions import BadRequest, ResourceNotFound
from src.models import TonTransaction, User
from src.ton_transaction.tasks import ton_transaction_find_real_hash
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import (
    create_ton_transaction,
    create_transaction,
    rstr,
)


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


@pytest.mark.asyncio
async def test_lookup_sets_chain_hash_on_every_purchase_of_a_bulk(
    save_fixture: SaveFixture,
    session: AsyncSession,
    user: User,
    toncenter_mock: MagicMock,
    mocker: MockerFixture,
) -> None:
    purchases = []
    for _ in range(3):
        purchase = await create_transaction(
            save_fixture,
            user=user,
            ton_transaction=await create_ton_transaction(
                save_fixture, hash="external-hash"
            ),
        )
        purchase.outgoing_message_hash = "external-hash"
        await save_fixture(purchase)
        purchases.append(purchase)
    other = await create_ton_transaction(save_fixture, hash="other-hash")

    matching = MagicMock(spec=Transaction)
    matching.in_msg = MagicMock()
    matching.cell = MagicMock()
    matching.in_msg.is_external = True
    matching.cell.hash = b"found"
    mocker.patch("src.ton_transaction.tasks.Cell.one_from_boc")
    mocker.patch(
        "src.ton_transaction.tasks.Transaction.deserialize", return_value=matching
    )
    mocker.patch(
        "src.ton_transaction.tasks.normalize_hash", return_value="external-hash"
    )
    toncenter_mock.provider = MagicMock()
    toncenter_mock.provider.get_transactions = AsyncMock(
        return_value=MagicMock(result=[MagicMock(data="boc")])
    )

    await ton_transaction_find_real_hash(
        ton_transaction_id=purchases[0].ton_transaction_id, session=session
    )

    for purchase in purchases:
        await session.refresh(purchase)
        ton_transaction = await session.get(
            TonTransaction, purchase.ton_transaction_id, populate_existing=True
        )
        assert ton_transaction is not None
        assert ton_transaction.hash == b"found".hex()
        assert purchase.sent_at is not None
    await session.refresh(other)
    assert other.hash == "other-hash"


@pytest.mark.asyncio
async def test_deposit_chain_hash_stays_unique(save_fixture: SaveFixture) -> None:
    def deposit_transaction() -> TonTransaction:
        return TonTransaction(
            nano_amount=1,
            hash="incoming-hash",
            message_hash=None,
            from_address=rstr("someaddress"),
            to_address=rstr("someaddress"),
        )

    await save_fixture(deposit_transaction())
    with pytest.raises(IntegrityError):
        await save_fixture(deposit_transaction())
