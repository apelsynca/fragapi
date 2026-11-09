import random
from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture
from ton_core import (
    Address,
    Cell,
    ExternalMessage,
    begin_cell,
    cell_to_b64,
    to_amount,
    to_nano,
)

from src.enums import TransactionReason
from src.exceptions import FragRequestValidationError, InsufficientFunds
from src.fee import fee_calculator
from src.kit.pagination import PaginationParams
from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from src.kit.utils import utc_now
from src.models import User
from src.postgres import AsyncSession
from src.transaction.models import FTMetadata
from src.transaction.repository import TransactionRepository
from src.transaction.service import transaction as transaction_service
from src.transaction.sorting import TransactionSortProperty
from src.transaction.tasks import fragment_transaction_process
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import (
    create_ton_transaction,
    create_transaction,
    create_user,
    get_tc_transaction,
)
from tests.fixtures.ton_connect import get_valid_tc_msg

# NOTE: maybe more tests here


@pytest.fixture
def enqueue_task_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.transaction.service.enqueue_task")


@pytest.mark.asyncio
async def test_create_from_tc_raises_validation_if_no_msgs(
    session: AsyncSession, user: User
) -> None:
    tc_transaction = get_tc_transaction(messages=[])
    with pytest.raises(FragRequestValidationError):
        await transaction_service._create_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=TransactionReason.stars,
            metadata=FTMetadata(recipient="", recipient_username=""),
        )


@pytest.mark.asyncio
async def test_create_from_tc_raises_validation_if_2_msgs(
    session: AsyncSession, user: User
) -> None:
    tc_transaction = get_tc_transaction(
        messages=[get_valid_tc_msg(amount=19.2), get_valid_tc_msg(amount=5.12)]
    )
    with pytest.raises(FragRequestValidationError):
        await transaction_service._create_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=TransactionReason.stars,
            metadata=FTMetadata(recipient="", recipient_username=""),
        )


@pytest.mark.asyncio
async def test_creates_from_tc_with_valid_data(
    session: AsyncSession, valid_tc_transaction: TonConnectTransaction, user: User
) -> None:
    tc_msg = valid_tc_transaction.messages[0]
    assert tc_msg.payload

    transaction = await transaction_service._create_from_tc(
        session=session,
        tc_transaction=valid_tc_transaction,
        user=user,
        reason=TransactionReason.stars,
        metadata=FTMetadata(
            recipient="recipientXrecipient",
            recipient_username="homocitrus",
            stars_amount=52,  # better handle from metadata
        ),
    )

    assert transaction.user == user
    assert transaction.amount == fee_calculator.total_cost(
        float(to_amount(tc_msg.amount))
    )
    assert transaction.recipient == "recipientXrecipient"
    assert transaction.recipient_username == "homocitrus"
    assert transaction.stars_amount == 52

    btransa = transaction.ton_transaction
    assert btransa is not None
    assert btransa.nano_amount == tc_msg.amount
    assert btransa.hash is None
    assert btransa.message_hash is not None
    assert btransa.from_address == valid_tc_transaction.from_address
    assert btransa.to_address == Address(tc_msg.address).to_str(is_user_friendly=False)


@pytest.mark.asyncio
async def test_creates_from_tc_with_right_message_hash(
    session: AsyncSession, valid_tc_transaction: TonConnectTransaction, user: User
) -> None:
    tc_msg = valid_tc_transaction.messages[0]
    assert tc_msg.payload

    padded_payload = tc_msg.payload + "=" * (-len(tc_msg.payload) % 4)
    cell = Cell.one_from_boc(padded_payload)
    message = ExternalMessage(dest=Address(tc_msg.address), body=cell)

    fragment_transaction = await transaction_service._create_from_tc(
        session=session,
        tc_transaction=valid_tc_transaction,
        user=user,
        reason=TransactionReason.premium,
        metadata=FTMetadata(
            recipient="random",
            recipient_username="apelsin",
            premium_months=3,
        ),
    )
    transaction = fragment_transaction.ton_transaction
    assert transaction is not None

    assert transaction.message_hash == message.normalized_hash
    assert transaction.hash is None


@pytest.mark.asyncio
async def test_creates_in_db(
    session: AsyncSession, valid_tc_transaction: TonConnectTransaction, user: User
) -> None:
    await transaction_service._create_from_tc(
        session=session,
        tc_transaction=valid_tc_transaction,
        user=user,
        reason=TransactionReason.premium,
        metadata=FTMetadata(
            recipient="X-x-xrecipientXrecipientx-x-X",
            recipient_username="homocitrus",
            premium_months=3,
        ),
    )

    repository = TransactionRepository.from_session(session)
    transactions = await repository.get_all(stmt=repository.get_base_stmt())

    assert len(transactions) == 1
    assert transactions[0].user == user
    assert transactions[0].recipient_username == "homocitrus"


@pytest.mark.asyncio
@pytest.mark.parametrize("amount", [10, 1.032, 0.39258, 862])
async def test_removes_money_from_user_with_fee(
    session: AsyncSession, user: User, amount: float, enqueue_task_mock: MagicMock
) -> None:
    tc_transaction = get_tc_transaction(
        messages=[
            TonConnectMessage(
                address="UQDm89iCT0ax77q5r8aEeTQoxV_tabRqFaSb5popvEnlMO6e",
                amount=to_nano(amount),
                payload="te6ccgEBAQEAJwAASgAAAAA1MCBUZWxlZ3JhbSBTdGFycyAKClJlZiN4Z01NbTM3bVY",
            )
        ]
    )

    user.balance = amount + 100
    await session.flush()

    transaction = await transaction_service.send_from_tc(
        session=session,
        tc_transaction=tc_transaction,
        user=user,
        reason=TransactionReason.stars,
        metadata=FTMetadata(
            recipient="X-x-xrecipientXrecipientx-x-X",
            recipient_username="homocitrus",
            stars_amount=52,
        ),
    )
    assert transaction is not None

    expect = amount + 100 - fee_calculator.total_cost(amount)
    assert user.balance == expect

    enqueue_task_mock.assert_called_once_with(
        fragment_transaction_process,
        transaction_id=transaction.id,
        tc_transaction=tc_transaction,
    )


@pytest.mark.asyncio
async def test_lists_transactions_right_user(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    for _ in range(3):
        transaction = await create_ton_transaction(
            save_fixture, amount=random.randint(1, 100)
        )
        await create_transaction(save_fixture, user=user, ton_transaction=transaction)

    user_second = await create_user(save_fixture)
    transactiond = await create_ton_transaction(
        save_fixture, amount=random.randint(1, 100)
    )
    await create_transaction(
        save_fixture, user=user_second, ton_transaction=transactiond
    )

    sorting = [(TransactionSortProperty.created_at, True)]
    pagination = PaginationParams(page=1, limit=100)

    items, count = await transaction_service.fetch_list(
        session=session, user=user, pagination=pagination, sorting=sorting
    )

    assert len(items) == 3
    assert count == len(items)
    assert items[0].ton_transaction  # test getattr


@pytest.mark.asyncio
async def test_get_stats_empty(session: AsyncSession, user: User) -> None:
    stats = await transaction_service.get_stats(session=session, user=user)

    assert stats.total_spend == 0
    assert stats.stars_total_spend == 0
    assert stats.premium_total_spend == 0


@pytest.mark.asyncio
async def test_gets_stats_right_amount(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    transaction1 = await create_ton_transaction(save_fixture, amount=5.252)
    await create_transaction(
        save_fixture, user=user, ton_transaction=transaction1, amount=4.25
    )

    transaction2 = await create_ton_transaction(save_fixture, amount=5.252)
    await create_transaction(
        save_fixture,
        user=user,
        ton_transaction=transaction2,
        amount=2.1,
        premium_months=3,
    )

    stats = await transaction_service.get_stats(session=session, user=user)

    assert stats.total_spend == 6.35
    assert stats.stars_total_spend == 4.25
    assert stats.premium_total_spend == 2.1


@freeze_time("2026-12-12 12:00:00")
@pytest.mark.asyncio
async def test_chart_data_counts_stars_and_premium_in_window(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    now = utc_now()

    stars = await create_transaction(
        save_fixture,
        user=user,
        ton_transaction=await create_ton_transaction(save_fixture),
        amount=1.5,
    )
    premium = await create_transaction(
        save_fixture,
        user=user,
        ton_transaction=await create_ton_transaction(save_fixture),
        amount=2.25,
        premium_months=3,
    )
    out_of_window = await create_transaction(
        save_fixture,
        user=user,
        ton_transaction=await create_ton_transaction(save_fixture),
        amount=7,
    )
    stars.created_at = now
    premium.created_at = now
    out_of_window.created_at = now - timedelta(days=100)
    await session.flush()

    points = await transaction_service.get_chart_data(session=session, user=user)

    assert len(points) == 90
    assert points[-1].date == now.date()
    assert points[-1].stars_spend == 1.5
    assert points[-1].premium_spend == 2.25
    assert sum(p.stars_spend for p in points) == 1.5
    assert sum(p.premium_spend for p in points) == 2.25


@pytest.mark.asyncio
async def test_bulk_charge_debits_what_balance_covers(
    session: AsyncSession, user: User, enqueue_task_mock: MagicMock
) -> None:
    tc_transactions = [
        get_tc_transaction(messages=[get_valid_tc_msg(amount=amount)])
        for amount in (10, 50, 5)
    ]
    for i, tc_transaction in enumerate(tc_transactions):
        # Distinct payloads, message hashes are unique.
        tc_transaction.messages[0].payload = cell_to_b64(
            begin_cell().store_uint(i, 32).end_cell()
        )
    user.balance = 20
    await session.flush()

    results = await transaction_service.charge_bulk_from_tc(
        session=session,
        user=user,
        reason=TransactionReason.stars,
        purchases=[
            (tc, FTMetadata(recipient="r", recipient_username="u", stars_amount=50))
            for tc in tc_transactions
        ],
    )

    first, second, third = results
    assert isinstance(second, InsufficientFunds)
    assert not isinstance(first, InsufficientFunds)
    assert not isinstance(third, InsufficientFunds)
    # Flushed: callers store and send them by id.
    assert first.id is not None
    assert third.id is not None
    assert user.balance == pytest.approx(
        20 - fee_calculator.total_cost(10) - fee_calculator.total_cost(5)
    )
    # Sending is the caller's job, in one message for the whole batch.
    enqueue_task_mock.assert_not_called()


@pytest.mark.asyncio
async def test_bulk_charge_debits_nothing_if_nothing_is_affordable(
    session: AsyncSession, user: User, enqueue_task_mock: MagicMock
) -> None:
    user.balance = 0
    await session.flush()

    results = await transaction_service.charge_bulk_from_tc(
        session=session,
        user=user,
        reason=TransactionReason.stars,
        purchases=[
            (
                get_tc_transaction(messages=[get_valid_tc_msg(amount=1)]),
                FTMetadata(recipient="r", recipient_username="u", stars_amount=50),
            )
        ],
    )

    assert isinstance(results[0], InsufficientFunds)
    assert user.balance == 0
