import random
import string
from datetime import datetime

import pytest_asyncio
from ton_core import to_nano

from src.fragment_rest.types import FoundRecipientData, RecipientData
from src.models import Transaction, User
from src.models.transactions import TransactionReason, TransactionStatus
from src.wallet.types import TonConnectMessage, TonConnectTransaction
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


async def create_transaction(
    save_fixture: SaveFixture,
    user: User,
    reason: TransactionReason = TransactionReason.STARS,
    status: TransactionStatus = TransactionStatus.PENDING,
    *,
    amount: float | None = None,
    recipient: str | None = None,
) -> Transaction:
    transaction = Transaction(
        amount=random.randint(1, 10000) / 100 if amount is None else amount,
        reason=reason,
        status=status,
        recipient=rstr("recipient") if recipient is None else recipient,
        user=user,
    )
    await save_fixture(transaction)
    return transaction


def get_fake_recipient_data() -> RecipientData:
    return RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=False,
            recipient=rstr("XXxaaAxXXxXXxxXXXxxA"),
            photo=rstr("img"),
            name=rstr("Homo Citrus"),
        ),
    )


def get_valid_transaction(amount: float) -> TonConnectTransaction:
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
