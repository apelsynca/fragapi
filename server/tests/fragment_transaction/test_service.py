import random

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Address, Cell, ExternalMessage, to_amount, to_nano

from src.fee import after_fee, after_ton_network_fee
from src.fragment_transaction.models import FTMetadata
from src.fragment_transaction.repository import FragmentTransactionRepository
from src.fragment_transaction.service import (
    fragment_transaction as fragment_transaction_service,
)
from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from src.models import User
from src.models.fragment_transactions import FragmentTransactionReason
from tests.fixtures.random_objects import RANDOM_TON_ADDRESSES, get_tc_transaction


@pytest.fixture
def tc_transaction() -> TonConnectTransaction:
    return get_tc_transaction(
        messages=[
            TonConnectMessage(
                address=random.choice(RANDOM_TON_ADDRESSES),
                amount=to_nano(5.25),
                payload="te6ccgEBAQEAJwAASgAAAAA1MCBUZWxlZ3JhbSBTdGFycyAKClJlZiN4Z01NbTM3bVY",
            )
        ]
    )


@pytest.mark.asyncio
async def test_creates_from_tc_with_valid_data(
    session: AsyncSession, tc_transaction: TonConnectTransaction, user: User
) -> None:
    tc_msg = tc_transaction.messages[0]
    assert tc_msg.payload

    fragment_transaction = await fragment_transaction_service._create_from_tc(
        session=session,
        tc_transaction=tc_transaction,
        user=user,
        reason=FragmentTransactionReason.stars,
        metadata=FTMetadata(
            recipient="recipientXrecipient",
            recipient_username="homocitrus",
            stars_amount=52,  # better handle from metadata
        ),
    )

    assert fragment_transaction.user == user
    assert fragment_transaction.amount >= float(to_amount(tc_msg.amount))
    assert fragment_transaction.recipient == "recipientXrecipient"
    assert fragment_transaction.recipient_username == "homocitrus"
    assert fragment_transaction.stars_amount == 52

    btransa = fragment_transaction.transaction
    assert btransa is not None
    assert btransa.nano_amount == tc_msg.amount
    assert btransa.hash is None
    assert btransa.message_hash is not None
    assert btransa.from_address == tc_transaction.from_address
    assert btransa.to_address == Address(tc_msg.address).to_str(is_user_friendly=False)


@pytest.mark.asyncio
async def test_creates_from_tc_with_right_message_hash(
    session: AsyncSession, tc_transaction: TonConnectTransaction, user: User
) -> None:
    tc_msg = tc_transaction.messages[0]
    assert tc_msg.payload

    padded_payload = tc_msg.payload + "=" * (-len(tc_msg.payload) % 4)
    cell = Cell.one_from_boc(padded_payload)
    message = ExternalMessage(dest=Address(tc_msg.address), body=cell)

    fragment_transaction = await fragment_transaction_service._create_from_tc(
        session=session,
        tc_transaction=tc_transaction,
        user=user,
        reason=FragmentTransactionReason.premium,
        metadata=FTMetadata(
            recipient="random",
            recipient_username="apelsin",
            premium_months=3,
        ),
    )
    transaction = fragment_transaction.transaction
    assert transaction is not None

    assert transaction.message_hash == message.normalized_hash
    assert transaction.hash is None


@pytest.mark.asyncio
async def test_creates_in_db(
    session: AsyncSession, tc_transaction: TonConnectTransaction, user: User
) -> None:
    await fragment_transaction_service._create_from_tc(
        session=session,
        tc_transaction=tc_transaction,
        user=user,
        reason=FragmentTransactionReason.premium,
        metadata=FTMetadata(
            recipient="X-x-xrecipientXrecipientx-x-X",
            recipient_username="homocitrus",
            premium_months=3,
        ),
    )

    repository = FragmentTransactionRepository.from_session(session)
    transactions = await repository.get_all(stmt=repository.get_base_stmt())

    assert len(transactions) == 1
    assert transactions[0].user == user
    assert transactions[0].recipient_username == "homocitrus"


@pytest.mark.asyncio
async def test_removes_money_from_user_with_fee(
    session: AsyncSession, user: User
) -> None:
    tc_transaction = get_tc_transaction(
        messages=[
            TonConnectMessage(
                address=random.choice(RANDOM_TON_ADDRESSES),
                amount=to_nano(10),
                payload="te6ccgEBAQEAJwAASgAAAAA1MCBUZWxlZ3JhbSBTdGFycyAKClJlZiN4Z01NbTM3bVY",
            )
        ]
    )

    user.balance = 125

    await fragment_transaction_service.from_tc(
        session=session,
        tc_transaction=tc_transaction,
        user=user,
        reason=FragmentTransactionReason.stars,
        metadata=FTMetadata(
            recipient="X-x-xrecipientXrecipientx-x-X",
            recipient_username="homocitrus",
            stars_amount=52,
        ),
    )

    assert user.balance < 125 - after_fee(after_ton_network_fee(10))
