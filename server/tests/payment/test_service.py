import random

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_amount

from src.config import settings
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.models import User
from src.models.payments import PaymentStatus
from src.payment.repository import PaymentRepository
from src.payment.service import payment as payment_service
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_payment, create_transaction, rstr


@pytest.mark.asyncio
async def test_creates_right(session: AsyncSession, user: User) -> None:
    payment = await payment_service.create(
        session=session,
        user=user,
        amount=settings.MIN_TON_DEPOSIT_AMOUNT + random.randint(1, 10),
    )

    repository = PaymentRepository.from_session(session)
    found_pay = await repository.get_by_id(id=payment.id)

    assert found_pay is not None
    assert found_pay.user == user


@pytest.mark.asyncio
async def test_raises_if_less_than_min_dep_amount(
    session: AsyncSession, user: User
) -> None:
    with pytest.raises(BadRequest):
        await payment_service.create(
            session=session, user=user, amount=settings.MIN_TON_DEPOSIT_AMOUNT - 0.05
        )


@pytest.mark.asyncio
async def test_raises_not_found_if_not_found(
    save_fixture: SaveFixture, session: AsyncSession
) -> None:
    transaction = await create_transaction(
        save_fixture, amount=0.1, message_hash=rstr("any")
    )

    with pytest.raises(ResourceNotFound):
        await payment_service.complete_ton(
            session=session, transaction=transaction, hash=rstr("some")
        )


# might do with initial balance set, idk why


@pytest.mark.asyncio
async def test_abc():
    pass


@pytest.mark.asyncio
@pytest.mark.parametrize("amount", [0.25, 0.5, 2, 52.25, 102.2125, 999.9, 10000])
async def test_increases_users_balance(
    save_fixture: SaveFixture, session: AsyncSession, user: User, amount: float
) -> None:
    assert user.balance == 0

    if amount < settings.MIN_TON_DEPOSIT_AMOUNT:
        raise RuntimeError("Skipped since too low")  # lol :)

    payment_amount = amount

    hash = rstr("somehash")
    payment = await create_payment(
        save_fixture=save_fixture, user=user, amount=payment_amount, hash=hash
    )
    transaction = await create_transaction(
        save_fixture, amount=payment_amount, message_hash="xxx0xxx"
    )

    await payment_service.complete_ton(
        session=session, transaction=transaction, hash=hash
    )

    assert user.balance == payment.amount
    assert user.balance == float(to_amount(transaction.nano_amount))

    # And
    payment.status = PaymentStatus.pending
    with pytest.raises(FragError, match="Payment already has transaction"):
        await payment_service.complete_ton(
            session=session, transaction=transaction, hash=hash
        )


@pytest.mark.asyncio
async def test_raises_bad_different_amounts(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    assert user.balance == 0

    hash = rstr("somehash")
    await create_payment(
        save_fixture=save_fixture,
        user=user,
        amount=settings.MIN_TON_DEPOSIT_AMOUNT + random.randint(1, 10),
        hash=hash,
    )
    transaction = await create_transaction(
        save_fixture,
        amount=settings.MIN_TON_DEPOSIT_AMOUNT + random.randint(20, 99),
        message_hash="xxx0xxx",
    )

    with pytest.raises(BadRequest):
        await payment_service.complete_ton(
            session=session, transaction=transaction, hash=hash
        )

    assert user.balance == 0
