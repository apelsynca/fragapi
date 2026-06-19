import random
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.fragment_transactions.tasks import (
    DAILY_LOG_TEXT,
    fragment_transactions_log_daily_stats,
)
from src.backoffice.telegram_logs.tasks import telegram_log_send
from src.kit.utils import utc_now
from src.models import FragmentTransaction, User
from src.models.fragment_transactions import FragmentTransactionReason
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_transaction, rstr


async def create_fragment_transaction(
    save_fixture: SaveFixture,
    user: User,
    *,
    amount: float | None = None,
    created_at: datetime | None = None,
) -> FragmentTransaction:
    # message_hash valid?
    transaction = await create_transaction(save_fixture, amount=amount)

    frag_t = FragmentTransaction(
        user=user,
        recipient=rstr("recipient"),
        recipient_username=rstr("username"),
        amount=amount if amount is not None else random.randint(1, 250) / 100,
        ton_transaction=transaction,
        reason=FragmentTransactionReason.stars,
        created_at=utc_now() if created_at is None else created_at,
    )
    await save_fixture(frag_t)

    return frag_t


@pytest.fixture
def enqueue_task_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.backoffice.fragment_transactions.tasks.enqueue_task")


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

    await create_fragment_transaction(save_fixture, user, amount=5.25)
    await create_fragment_transaction(
        save_fixture, user, amount=5.25, created_at=yesterday_dt
    )
    await create_fragment_transaction(
        save_fixture,
        user_second,
        amount=2.50,
        created_at=yesterday_dt - timedelta(minutes=52),
    )
    await create_fragment_transaction(
        save_fixture,
        user_second,
        amount=3.25,
        created_at=yesterday_dt - timedelta(days=1),
    )

    await fragment_transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            amount=7.75,
            transactions_count=2,
            unique_users=2,
        ),
        with_notification=False,
    )


@freeze_time("2026-12-12")
@pytest.mark.asyncio
async def test_log_empty_text(
    enqueue_task_mock: MagicMock, session: AsyncSession
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    await fragment_transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            amount=0,
            transactions_count=0,
            unique_users=0,
        ),
        with_notification=False,
    )
