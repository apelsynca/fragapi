from secrets import token_urlsafe

import pytest_asyncio

from src.models import Deposit, TonTransaction, User
from src.models.deposits import DepositStatus
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import rstr


@pytest_asyncio.fixture
async def deposit(save_fixture: SaveFixture, user: User) -> Deposit:
    return await create_deposit(save_fixture, user, amount=3.252, hash=rstr("phash"))


async def create_deposit(
    save_fixture: SaveFixture,
    user: User,
    amount: float,
    hash: str | None = None,
    completed: bool = False,
    ton_transaction: TonTransaction | None = None,
) -> Deposit:
    deposit = Deposit(
        user=user,
        amount=amount,
        hash=hash if hash is not None else token_urlsafe(32),
        status=DepositStatus.completed if completed else DepositStatus.pending,
        ton_transaction=ton_transaction,
    )
    await save_fixture(deposit)
    return deposit
