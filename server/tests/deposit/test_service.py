import base64
import random

import pytest
from pytest_mock import MockerFixture
from ton_core import begin_cell, to_amount

from src.config import settings
from src.deposit.repository import DepositRepository
from src.deposit.service import deposit as deposit_service
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.kit.pagination import PaginationParams
from src.models import User
from src.models.deposits import DepositStatus
from src.postgres import AsyncSession
from tests.deposit.conftest import create_deposit
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_transaction, rstr


@pytest.mark.asyncio
async def test_creates_right(session: AsyncSession, user: User) -> None:
    deposit = await deposit_service.create(
        session=session,
        user=user,
        amount=settings.MIN_TON_DEPOSIT_AMOUNT + random.randint(1, 10),
    )

    repository = DepositRepository.from_session(session)
    found_pay = await repository.get_by_id(id=deposit.id)

    assert found_pay is not None
    assert found_pay.user == user


@pytest.mark.asyncio
async def test_raises_if_less_than_min_dep_amount(
    session: AsyncSession, user: User
) -> None:
    with pytest.raises(BadRequest):
        await deposit_service.create(
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
        await deposit_service.complete_ton(
            session=session, transaction=transaction, ref_hash=rstr("some")
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("amount", [0.25, 0.5, 2, 52.25, 102.2125, 999.9, 10000])
async def test_increases_users_balance(
    save_fixture: SaveFixture, session: AsyncSession, user: User, amount: float
) -> None:
    assert user.balance == 0

    if amount < settings.MIN_TON_DEPOSIT_AMOUNT:
        raise RuntimeError("Skipped since too low")  # lol :)

    hash = rstr("somehash")
    deposit = await create_deposit(
        save_fixture=save_fixture, user=user, amount=amount, hash=hash
    )
    transaction = await create_transaction(
        save_fixture, amount=amount, message_hash="xxx0xxx"
    )

    await deposit_service.complete_ton(
        session=session, transaction=transaction, ref_hash=hash
    )

    assert user.balance == deposit.amount
    assert user.balance == float(to_amount(transaction.nano_amount))

    # And
    deposit.status = DepositStatus.pending
    with pytest.raises(FragError, match="Deposit already has transaction"):
        await deposit_service.complete_ton(
            session=session, transaction=transaction, ref_hash=hash
        )


@pytest.mark.asyncio
async def test_raises_bad_different_amounts(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    assert user.balance == 0

    hash = rstr("somehash")
    await create_deposit(
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
        await deposit_service.complete_ton(
            session=session, transaction=transaction, ref_hash=hash
        )

    assert user.balance == 0


# creating stuff
@pytest.mark.asyncio
async def test_create_ton_right_payload(
    session: AsyncSession, user: User, mocker: MockerFixture, save_fixture: SaveFixture
) -> None:
    ref_hash = "SomekingoF-Hashxx"
    deposit = await create_deposit(save_fixture, user=user, amount=6.251, hash=ref_hash)

    mocker.patch.object(deposit_service, "create", return_value=deposit)

    same_payload_cell = (
        begin_cell()
        .store_uint(0, 32)
        .store_snake_string(deposit_service.TON_COMMENT_TEMPLATE.format(ref_hash))
        .end_cell()
    )
    same_payload = base64.b64encode(same_payload_cell.to_boc()).decode("utf-8")

    deposit_req_msg = await deposit_service.create_ton(
        session=session, user=user, amount=6.251
    )

    assert deposit_req_msg.payload == same_payload


@pytest.mark.asyncio
async def test_fetch_list_gets_only_completed(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    await create_deposit(
        save_fixture, user=user, amount=random.randint(1, 100) / 10, completed=True
    )
    await create_deposit(
        save_fixture, user=user, amount=random.randint(1, 100) / 10, completed=True
    )
    await create_deposit(
        save_fixture, user=user, amount=random.randint(1, 100) / 10, completed=False
    )

    pagination = PaginationParams(page=1, limit=100)
    deposits, count = await deposit_service.fetch_list(
        session=session, user=user, pagination=pagination
    )

    assert len(deposits) == 2
    assert count == len(deposits)


@pytest.mark.asyncio
async def test_fetch_list_gets_transactions(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    transaction = await create_transaction(
        save_fixture, amount=2.5291, hash="Usual hashiie"
    )
    await create_deposit(
        save_fixture, user=user, amount=2.5291, completed=True, transaction=transaction
    )
    await create_deposit(save_fixture, user=user, amount=9.25, completed=False)

    pagination = PaginationParams(page=1, limit=100)
    deposits, _ = await deposit_service.fetch_list(
        session=session, user=user, pagination=pagination
    )

    assert deposits[0].transaction is not None
    assert deposits[0].transaction.hash == "Usual hashiie"
