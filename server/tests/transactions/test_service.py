from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.kit.utils import utc_now
from src.models import User
from src.models.transactions import Transaction, TransactionReason, TransactionStatus
from src.transactions.repository import TransactionRepository
from src.transactions.schemas import TransactionChartPoint
from src.transactions.service import transaction as transaction_service
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_transaction, rstr


async def _create_transaction(
    save_fixture: SaveFixture,
    amount: float,
    user: User,
    reason: TransactionReason = TransactionReason.STARS,
    status: TransactionStatus = TransactionStatus.PENDING,
    days_from_now: int = 0,
) -> Transaction:
    transaction = Transaction(
        amount=amount,
        user=user,
        reason=reason,
        status=status,
        recipient=rstr("mockrecipient"),
        created_at=utc_now() - timedelta(days=days_from_now),
    )
    await save_fixture(transaction)
    return transaction


def empty_chart_stats() -> list[TransactionChartPoint]:
    today = utc_now().date()

    start_date = today - timedelta(days=90)

    fakedata = []
    for i in range(1, 90 + 1):
        fakedata.append(
            TransactionChartPoint(
                date=start_date + timedelta(days=i),
                ton_amount=0,
                transactions_count=0,
            )
        )

    return fakedata


@pytest.mark.asyncio
async def test_get_stats_for_right_user(
    session: AsyncSession, user: User, user_second: User, save_fixture: SaveFixture
) -> None:
    repository = TransactionRepository.from_session(session)
    stmt = repository.get_base_stmt()

    transactions_count = await repository.count(stmt=stmt)
    assert transactions_count == 0

    for _ in range(5):
        await create_transaction(
            save_fixture, user=user, reason=TransactionReason.STARS
        )

    for _ in range(3):
        await create_transaction(save_fixture, user=user_second)

    stats = await transaction_service.get_stats(session, user)

    assert stats.stars_purchases_count == 5

    stmt = repository.get_base_stmt().where(Transaction.user == user)
    transactions_count = await repository.count(stmt=stmt)
    assert transactions_count == 5


@pytest.mark.asyncio
async def test_get_stats_correct_purchases_count(
    session: AsyncSession, user: User, save_fixture: SaveFixture
) -> None:
    repository = TransactionRepository.from_session(session)
    stmt = repository.get_base_stmt()

    transactions_count = await repository.count(stmt=stmt)
    assert transactions_count == 0

    for _ in range(5):
        await create_transaction(
            save_fixture, user=user, reason=TransactionReason.STARS
        )

    stats = await transaction_service.get_stats(session, user)

    assert stats.stars_purchases_count == 5

    transactions_count = await repository.count(stmt=stmt)
    assert transactions_count == 5


@pytest.mark.asyncio
async def test_get_chart_stats_ignores_over_90days(
    session: AsyncSession, user: User, save_fixture: SaveFixture
) -> None:
    await save_fixture(
        Transaction(
            amount=100,
            user=user,
            reason=TransactionReason.PREMIUM,
            status=TransactionStatus.COMPLETED,
            recipient=rstr("abc"),
            created_at=utc_now() - timedelta(days=120),
        )
    )
    await save_fixture(
        Transaction(
            amount=225,
            user=user,
            reason=TransactionReason.STARS,
            status=TransactionStatus.COMPLETED,
            recipient=rstr("abc"),
        )
    )

    expected = empty_chart_stats()
    expected[-1] = TransactionChartPoint(
        date=utc_now().date(), ton_amount=225, transactions_count=1
    )

    chart_stats = await transaction_service.get_chart_stats(session, user)

    assert len(chart_stats) == 90
    assert chart_stats[-1] == expected[-1]


@pytest.mark.asyncio
async def test_get_chart_stats_only_include_completed(
    session: AsyncSession, user: User, save_fixture: SaveFixture
) -> None:
    today = utc_now().date()

    await _create_transaction(
        save_fixture,
        amount=4.12,
        user=user,
        reason=TransactionReason.PREMIUM,
        status=TransactionStatus.COMPLETED,
        days_from_now=1,
    )
    await _create_transaction(
        save_fixture,
        amount=3.12,
        user=user,
        reason=TransactionReason.STARS,
        status=TransactionStatus.COMPLETED,
        days_from_now=1,
    )
    await _create_transaction(
        save_fixture,
        amount=4,
        user=user,
        days_from_now=1,
    )
    await _create_transaction(
        save_fixture,
        amount=4,
        user=user,
        days_from_now=1,
        status=TransactionStatus.FAILED,
    )

    chart_stats = await transaction_service.get_chart_stats(session, user)

    assert chart_stats[-2] == TransactionChartPoint(
        date=today - timedelta(days=1), ton_amount=7.24, transactions_count=2
    )


@pytest.mark.asyncio
async def test_get_chart_stats_gives_90_empty_items(
    session: AsyncSession, user: User
) -> None:
    chart_stats = await transaction_service.get_chart_stats(session, user)

    expected = empty_chart_stats()

    assert len(chart_stats) == 90
    assert chart_stats == expected


@pytest.mark.asyncio
async def test_get_chart_stats_all_spend_monthly(
    session: AsyncSession, user: User, save_fixture: SaveFixture
) -> None:
    transaction = Transaction(
        amount=10,
        reason=TransactionReason.STARS,
        status=TransactionStatus.PENDING,
        recipient=rstr("reci"),
        user=user,
        created_at=utc_now() - timedelta(days=33),
    )
    await save_fixture(transaction)
    transaction = Transaction(
        amount=10,
        reason=TransactionReason.STARS,
        status=TransactionStatus.PENDING,
        recipient=rstr("reci"),
        user=user,
    )
    await save_fixture(transaction)
    transaction = Transaction(
        amount=3,
        reason=TransactionReason.PREMIUM,
        status=TransactionStatus.PENDING,
        recipient=rstr("reci"),
        user=user,
        created_at=utc_now() - timedelta(days=3),
    )
    await save_fixture(transaction)
    transaction = Transaction(
        amount=2.52,
        reason=TransactionReason.PREMIUM,
        status=TransactionStatus.COMPLETED,
        recipient=rstr("reci"),
        user=user,
    )
    await save_fixture(transaction)

    stats = await transaction_service.get_stats(session=session, user=user)

    assert stats.monthly_spend == 15.52
    assert stats.stars_monthly_spend == 10
    assert stats.premium_monthly_spend == 5.52
