import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.models.transactions import Transaction, TransactionReason
from src.transactions.repository import TransactionRepository
from src.transactions.service import transaction as transaction_service
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_transaction


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
