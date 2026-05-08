import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import ResourceNotFound
from src.models import User
from src.payments.service import payment as payment_service
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_payment


@pytest.mark.asyncio
async def test_processes_ton_payment(
    save_fixture: SaveFixture, user: User, session: AsyncSession
) -> None:
    assert user.balance == 0
    await create_payment(save_fixture, user=user, amount=6.2645, hash="myhash")

    await payment_service.process_ton_payment(session=session, hash="myhash")
    assert user.balance == 6.2645


@pytest.mark.asyncio
async def test_processes_ton_payment_raises_if_not_found(
    save_fixture: SaveFixture, user: User, session: AsyncSession
) -> None:
    assert user.balance == 0
    await create_payment(save_fixture, user=user, amount=6.2645, hash="different_hash")

    with pytest.raises(ResourceNotFound):
        await payment_service.process_ton_payment(session=session, hash="myhash")

    assert user.balance == 0
