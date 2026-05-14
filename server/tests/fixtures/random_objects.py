import random
import string
from datetime import datetime
from secrets import token_urlsafe

import pytest_asyncio
from ton_core import to_nano

from src.kit.ton_connect import TonConnectMessage
from src.models import Payment, User
from src.wallet.types import TonConnectTransaction
from tests.fixtures.database import SaveFixture


def rstr(prefix: str) -> str:
    return prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def lstr(suffix: str) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6)) + suffix


@pytest_asyncio.fixture
async def user(save_fixture: SaveFixture) -> User:
    return await create_user(save_fixture)


@pytest_asyncio.fixture
async def user_second(save_fixture: SaveFixture) -> User:
    return await create_user(save_fixture)


async def create_user(save_fixture: SaveFixture) -> User:
    user = User(first_name=rstr("Mock"), username=rstr("test_"))
    await save_fixture(user)
    return user


def get_valid_tc_transaction(amount: float) -> TonConnectTransaction:
    return get_tc_transaction(
        messages=[
            TonConnectMessage(
                address=rstr("mockaddress"),
                amount=to_nano(amount),
                payload="TrustMeBroValidPayload",
            )
        ]
    )


def get_tc_transaction(messages: list[TonConnectMessage] = []) -> TonConnectTransaction:
    return TonConnectTransaction(
        valid_until=datetime(year=2000, month=3, day=1),
        from_address="EQxxx",
        messages=messages,
    )


async def create_payment(
    save_fixture: SaveFixture, user: User, amount: float, hash: str | None = None
) -> Payment:
    payment = Payment(
        user=user, amount=amount, hash=hash if hash is not None else token_urlsafe(32)
    )
    await save_fixture(payment)
    return payment
