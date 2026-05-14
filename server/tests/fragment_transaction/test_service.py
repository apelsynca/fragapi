import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.fragment_transaction.service import (
    fragment_transaction as fragment_transaction_service,
)
from src.models import Transaction, User
from src.models.fragment_transactions import FragmentTransactionReason


@pytest.mark.asyncio
async def test_abc(session: AsyncSession, user: User, transaction: Transaction) -> None:
    transa = await fragment_transaction_service.create(
        session=session,
        user=user,
        amount=1.2352,
        recipient="somerecipient",
        username="someonezz",
        transaction=transaction,
        reason=FragmentTransactionReason.stars,
    )

    assert transa.amount == 1.2352
    assert transa.username == "someonezz"
    assert transa.recipient == "somerecipient"
    assert transa.transaction == transaction
