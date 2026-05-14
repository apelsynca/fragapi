import random
import string
from datetime import datetime
from secrets import token_urlsafe
from unittest.mock import MagicMock

import pytest_asyncio
from pytonapi.rest.models import AccountAddress
from pytonapi.rest.models import Message as TonAPIMessage
from pytonapi.rest.models import Transaction as TonAPITransaction
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


def create_tonapi_transaction_mock(
    hash: str = "xxxxxxe0b494f5a8f7c94f8ab37816e98be1a4a95b97c8daeba262e04975cb6c",
    success: bool = True,
    in_msg_type: str = "int_msg",
    value: int = 0,
    destination_address_raw: str
    | None = "0:69061ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebc9f",
    source_address_raw: str | None = None,
    out_msgs: list = [],
) -> MagicMock:
    tonapi_transaction = MagicMock(spec=TonAPITransaction)
    tonapi_transaction.hash = hash
    tonapi_transaction.lt = 1
    tonapi_transaction.success = success  # test that raises
    tonapi_transaction_in_msg = MagicMock(spec=TonAPIMessage)
    tonapi_transaction_in_msg.msg_type = in_msg_type  # test that raises
    tonapi_transaction_in_msg.value = value

    tonapi_transaction_in_msg.destination = None
    if destination_address_raw is not None:
        tonapi_transaction_in_msg.destination = AccountAddress(
            address=destination_address_raw,
            is_scam=False,
            is_wallet=True,
        )

    tonapi_transaction_in_msg.source = None
    if source_address_raw is not None:
        tonapi_transaction_in_msg.source = AccountAddress(
            address=source_address_raw, is_scam=False, is_wallet=True
        )

    tonapi_transaction.in_msg = tonapi_transaction_in_msg
    tonapi_transaction.out_msgs = out_msgs  # test that raises if not len 0

    return tonapi_transaction
