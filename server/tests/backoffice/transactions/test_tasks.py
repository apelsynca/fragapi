import random
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.telegram_logs.tasks import telegram_log_send
from src.backoffice.transactions.tasks import (
    DAILY_LOG_TEXT,
    transactions_log_daily_stats,
)
from src.enums import TransactionReason
from src.fee import approx_before_fee
from src.kit.utils import utc_now
from src.models import Transaction, User
from src.models.deposits import Deposit, DepositStatus
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction, rstr


async def create_user(save_fixture: SaveFixture, *, balance: float = 0) -> User:
    user = User(first_name=rstr("Mock"), username=rstr("test_"), balance=balance)
    await save_fixture(user)
    return user


# only for dep test
async def create_deposit(
    save_fixture: SaveFixture, user: User, amount: float, created_at: datetime
) -> Deposit:
    deposit = Deposit(
        user=user,
        amount=amount,
        hash=rstr("mock_hash"),
        ton_transaction=None,
        status=DepositStatus.pending,
        created_at=created_at,
    )
    await save_fixture(deposit)
    return deposit


async def create_transaction(
    save_fixture: SaveFixture,
    user: User,
    *,
    amount: float | None = None,
    created_at: datetime | None = None,
) -> Transaction:
    # message_hash valid?
    transaction = await create_ton_transaction(save_fixture, amount=amount)

    frag_t = Transaction(
        user=user,
        recipient=rstr("recipient"),
        recipient_username=rstr("username"),
        amount=amount if amount is not None else random.randint(1, 250) / 100,
        ton_transaction=transaction,
        reason=TransactionReason.stars,
        created_at=utc_now() if created_at is None else created_at,
    )
    await save_fixture(frag_t)

    return frag_t


@pytest.fixture
def enqueue_task_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.backoffice.transactions.tasks.enqueue_task")


@freeze_time("2026-02-06")
@pytest.mark.asyncio
async def test_log_daily_stats_right_text(
    save_fixture: SaveFixture,
    enqueue_task_mock: MagicMock,
    user: User,
    user_second: User,
    session: AsyncSession,
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    await create_transaction(save_fixture, user, amount=5.25)
    await create_transaction(save_fixture, user, amount=5.25, created_at=yesterday_dt)
    await create_transaction(
        save_fixture,
        user_second,
        amount=2.50,
        created_at=yesterday_dt - timedelta(minutes=52),
    )
    await create_transaction(
        save_fixture,
        user_second,
        amount=3.25,
        created_at=yesterday_dt - timedelta(days=1),
    )

    await transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=0,
            volume=7.75,
            raw_commission_amount=approx_before_fee(7.75),
            transactions_count=2,
            transactions_unique_users=2,
            new_users_count=0,
            deposits_count=0,
            deposits_amount=0,
        ),
        with_notification=False,
    )


@freeze_time("2026-12-12")
@pytest.mark.asyncio
async def test_log_empty_text(
    enqueue_task_mock: MagicMock, session: AsyncSession
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    await transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=0,
            volume=0,
            raw_commission_amount=0,
            transactions_count=0,
            transactions_unique_users=0,
            new_users_count=0,
            deposits_count=0,
            deposits_amount=0,
        ),
        with_notification=False,
    )


@pytest.mark.asyncio
async def test_log_right_unique_users_and_total_balance(
    save_fixture: SaveFixture, enqueue_task_mock: MagicMock, session: AsyncSession
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    users = [
        await create_user(save_fixture, balance=3),
        await create_user(save_fixture, balance=1.07),
        await create_user(save_fixture, balance=1.05),
    ]

    for user in users:
        await create_transaction(save_fixture, user, amount=5, created_at=yesterday_dt)
        await create_transaction(save_fixture, user, amount=3, created_at=yesterday_dt)

    await transactions_log_daily_stats(session)

    users_count = len(users)
    enqueue_task_mock.assert_called_once_with(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=5.12,
            volume=8 * users_count,
            raw_commission_amount=approx_before_fee(8 * users_count),
            transactions_count=users_count * 2,
            transactions_unique_users=users_count,
            new_users_count=0,
            deposits_count=0,
            deposits_amount=0,
        ),
        with_notification=False,
    )


@pytest.mark.asyncio
async def test_log_right_new_users(
    save_fixture: SaveFixture, enqueue_task_mock: MagicMock, session: AsyncSession
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    for _ in range(3):  # create unique users
        user = User(
            first_name=rstr("Mock"), username=rstr("test_"), created_at=yesterday_dt
        )
        await save_fixture(user)

    await transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=0,
            volume=0,
            raw_commission_amount=0,
            transactions_count=0,
            transactions_unique_users=0,
            new_users_count=3,
            deposits_count=0,
            deposits_amount=0,
        ),
        with_notification=False,
    )


@pytest.mark.asyncio
async def test_log_right_new_deposits(
    save_fixture: SaveFixture,
    enqueue_task_mock: MagicMock,
    session: AsyncSession,
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    users = [
        User(first_name=rstr("mockName"), username="gennie", created_at=yesterday_dt),
        User(first_name=rstr("mockName"), username="bynnie", created_at=yesterday_dt),
        User(first_name=rstr("mockName"), username="vinnie", created_at=yesterday_dt),
    ]

    await create_deposit(
        save_fixture, user=users[0], amount=5.25, created_at=yesterday_dt
    )
    await create_deposit(save_fixture, user=users[0], amount=1.85, created_at=utc_now())
    await create_deposit(save_fixture, user=users[2], amount=3, created_at=yesterday_dt)
    await create_deposit(save_fixture, user=users[1], amount=1.11, created_at=utc_now())

    for user in users:
        await save_fixture(user)

    await transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=0,
            volume=0,
            raw_commission_amount=0,
            transactions_count=0,
            transactions_unique_users=0,
            new_users_count=3,
            deposits_count=2,
            deposits_amount=8.25,
        ),
        with_notification=False,
    )
