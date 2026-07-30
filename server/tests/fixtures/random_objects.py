import random
import string
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest_asyncio
from pytonapi.rest.models import AccountAddress
from pytonapi.rest.models import Message as TonAPIMessage
from pytonapi.rest.models import Transaction as TonAPITransaction
from ton_core import Address, to_nano

from src.enums import TransactionReason
from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from src.kit.utils import utc_now
from src.models import ApiToken, TonTransaction, Transaction, User
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


RANDOM_TON_ADDRESSES = [
    "EQCKmuA92vaaZzt2kKQKpPT3TWV7LsakJqCYFl2jqHQZ6R6_",
    "UQANtyTiJuWgo5cTdrVlzpTzhYD3Heg3ssPoeAW2dM2v6nR1",
    "UQDljKm7IVGJ8BhR50rnCEJ9nu7QPyJkX_MzF9u1PKSn2U9f",
    "UQDm89iCT0ax77q5r8aEeTQoxV_tabRqFaSb5popvEnlMO6e",
]


def get_tc_transaction(messages: list[TonConnectMessage] = []) -> TonConnectTransaction:
    return TonConnectTransaction(
        valid_until=utc_now() + timedelta(seconds=10),
        from_address=Address(random.choice(RANDOM_TON_ADDRESSES)).to_str(
            is_user_friendly=True
        ),
        messages=messages,
    )


def create_tonapi_transaction_mock(
    hash: str = "xxxxxxe0b494f5a8f7c94f8ab37816e98be1a4a95b97c8daeba262e04975cb6c",
    success: bool = True,
    in_msg_type: str = "in_msg",  # was int_msg
    value: int = 0,
    *,
    destination_address_raw: str
    | None = "0:69061ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebc9f",
    source_address_raw: str | None = None,
    out_msgs: list = [],
    comment: str | None = None,
    body_op_name: str | None = None,
) -> MagicMock:
    if comment and in_msg_type != "in_msg":
        raise RuntimeError("Somethin weird with comment and in_msg")

    in_msg = MagicMock(spec=TonAPIMessage)
    in_msg.msg_type = in_msg_type
    in_msg.value = value
    in_msg.destination = None

    if comment is not None:
        in_msg.decoded_body = {"text": comment}
        in_msg.decoded_op_name = body_op_name or "text_comment"
    elif body_op_name is not None:
        in_msg.decoded_op_name = body_op_name

    if destination_address_raw is not None:
        in_msg.destination = AccountAddress(
            address=destination_address_raw,
            is_scam=False,
            is_wallet=True,
        )

    in_msg.source = None
    if source_address_raw is not None:
        in_msg.source = AccountAddress(
            address=source_address_raw, is_scam=False, is_wallet=True
        )

    tonapi_tx_mock = MagicMock(spec=TonAPITransaction, autospec=True)
    tonapi_tx_mock.in_msg = in_msg
    tonapi_tx_mock.hash = hash
    tonapi_tx_mock.lt = 1
    tonapi_tx_mock.success = success

    tonapi_tx_mock.out_msgs = out_msgs

    return tonapi_tx_mock


@pytest_asyncio.fixture
async def ton_transaction(save_fixture: SaveFixture) -> TonTransaction:
    return await create_ton_transaction(save_fixture)


async def create_ton_transaction(
    save_fixture: SaveFixture,
    *,
    amount: float | None = None,
    message_hash: str | None = None,
    hash: str | None = None,
) -> TonTransaction:
    ton_transaction = TonTransaction(
        nano_amount=to_nano(random.randint(1, 100) / 10 if amount is None else amount),
        hash=hash,
        message_hash=message_hash if message_hash else rstr("somemsghash"),
        from_address=rstr("someaddress"),
        to_address=rstr("someaddress"),
    )
    await save_fixture(ton_transaction)
    return ton_transaction


# TODO: rename it
@pytest_asyncio.fixture
async def fragment_transaction(
    save_fixture: SaveFixture, user: User, ton_transaction: TonTransaction
) -> Transaction:
    return await create_transaction(
        save_fixture, user=user, ton_transaction=ton_transaction
    )


async def create_transaction(
    save_fixture: SaveFixture,
    user: User,
    ton_transaction: TonTransaction,
    *,
    amount: float | None = None,
    stars_amount: int | None = None,
    premium_months: int | None = None,
    recipient_username: str | None = None,
) -> Transaction:
    recipient_username = recipient_username if recipient_username else rstr("username")
    frag_trans = Transaction(
        user=user,
        recipient=rstr("recipient"),
        recipient_username=recipient_username,
        amount=amount if amount is not None else random.randint(1, 250) / 100,
        ton_transaction=ton_transaction,
        reason=TransactionReason.premium if premium_months else TransactionReason.stars,
        stars_amount=stars_amount,
        premium_months=premium_months,
    )
    await save_fixture(frag_trans)
    return frag_trans


async def create_api_token(
    save_fixture: SaveFixture,
    user: User,
    *,
    name: str | None = None,
    last_used_at: datetime | None = None,
    expires_at: datetime | None = None,
) -> ApiToken:
    token = ApiToken(
        name=name or rstr("TokenName"),
        user=user,
        last_used_at=last_used_at,
        expires_at=expires_at,
    )
    await save_fixture(token)
    return token
