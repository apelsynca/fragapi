from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_nano

from src.config import settings
from src.exceptions import FragError, FragRequestValidationError, InsuficcientFunds
from src.fee import TON_FEE, after_fee, after_ton_network_fee
from src.kit.ton_connect import TonConnectMessage
from src.models import TransactionReason, User
from src.payments.service import payment as payment_service
from src.transactions.repository import TransactionRepository
from tests.fixtures.random_objects import (
    get_tc_transaction,
    get_valid_transaction,
    rstr,
)


@pytest.mark.asyncio
async def test_from_transaction_calls_wallet_manager_right(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    user.balance = 100
    tc_transaction = get_valid_transaction(1)
    wallet_manager.get_balance.return_value = 100
    wallet_manager.transfer_from_tc.return_value = "WHATTHEHELLY"

    message_hash = await payment_service.from_tc_transaction(
        session=session,
        user=user,
        wallet_manager=wallet_manager,
        tc_transaction=tc_transaction,
        recipient="somerecipient",
        reason=TransactionReason.STARS,
    )

    wallet_manager.transfer_from_tc.assert_called_once_with(transaction=tc_transaction)
    assert message_hash == "WHATTHEHELLY"


@pytest.mark.asyncio
async def test_from_transaction_raises_if_insufficient_funds(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    assert user.balance == 0
    wallet_manager.get_balance.return_value = 50
    tc_transaction = get_valid_transaction(1.1)

    with pytest.raises(InsuficcientFunds):
        await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=tc_transaction,
            recipient="somerecipient",
            reason=TransactionReason.STARS,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_from_transaction_raises_if_wallet_balance_lower(
    session: AsyncSession,
    user: User,
    wallet_manager: MagicMock,
) -> None:
    user.balance = 1000.251
    wallet_manager.get_balance.return_value = 5.25
    transaction = get_valid_transaction(amount=25.25)

    with pytest.raises(FragError):
        await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=transaction,
            recipient="somerecipient",
            reason=TransactionReason.STARS,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_from_transaction_raises_if_no_message(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    user.balance = 50
    transa = get_tc_transaction(messages=[])

    with pytest.raises(FragRequestValidationError):
        await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=transa,
            recipient="somerecipient",
            reason=TransactionReason.STARS,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_from_transaction_raises_if_more_than_one_message(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    user.balance = 50
    wallet_manager.get_balance.return_value = 15.52
    transa = get_tc_transaction(
        messages=[
            TonConnectMessage(
                address=rstr("EQxxx"), amount=to_nano(12.52), payload=None
            ),
            TonConnectMessage(
                address=rstr("EQxxx"), amount=to_nano(95.52), payload=None
            ),
        ]
    )

    with pytest.raises(FragRequestValidationError):
        await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=transa,
            recipient="somerecipient",
            reason=TransactionReason.STARS,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_from_transaction_raises_if_payload_is_none(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    user.balance = 1000
    transa = get_tc_transaction(
        messages=[
            TonConnectMessage(address="EQxxx", amount=to_nano(10.25), payload=None)
        ]
    )
    wallet_manager.get_balance.return_value = 2000

    with pytest.raises(FragRequestValidationError) as exc_info:
        await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=transa,
            recipient="somerecipient",
            reason=TransactionReason.STARS,
        )

    assert len(exc_info.value.errors())
    assert "type" in exc_info.value.errors()[0]
    assert exc_info.value.errors()[0]["type"] == "value_error"


@pytest.mark.asyncio
async def test_subtracts_with_fee_from_users_balance(
    session: AsyncSession,
    user: User,
    wallet_manager: MagicMock,
) -> None:
    user.balance = 10.25
    transaction = get_valid_transaction(amount=2.5)
    wallet_manager.get_balance.return_value = 1000

    await payment_service.from_tc_transaction(
        session=session,
        user=user,
        wallet_manager=wallet_manager,
        tc_transaction=transaction,
        recipient="somerecipient",
        reason=TransactionReason.STARS,
    )

    price_on_network = 2.5 + TON_FEE
    price = price_on_network + price_on_network * settings.API_PRICE_MARKUP

    # 10.25 - 2.5 ...
    assert user.balance == 10.25 - price
    wallet_manager.transfer_from_tc.assert_called_once()


@pytest.mark.asyncio
async def test_buy_raises_frag_error_if_wallet_balance_plus_fee(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    settings.API_PRICE_MARKUP = 0

    user.balance = 500
    transaction = get_valid_transaction(amount=102.25)

    wallet_manager.get_balance.return_value = 102.25 + TON_FEE
    with pytest.raises(FragError):
        await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=transaction,
            recipient="somerecipient",
            reason=TransactionReason.STARS,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_creates_transaction(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    user.balance = 100
    wallet_manager.get_balance.return_value = 100
    tc_transaction = get_valid_transaction(3.25)

    repository = TransactionRepository.from_session(session)
    transactions = await repository.get_all(stmt=repository.get_base_stmt())
    assert len(transactions) == 0

    await payment_service.from_tc_transaction(
        session=session,
        user=user,
        wallet_manager=wallet_manager,
        tc_transaction=tc_transaction,
        recipient="MySuperCoolFakeRecipient",
        reason=TransactionReason.PREMIUM,
    )

    transactions = await repository.get_all(stmt=repository.get_base_stmt())
    assert len(transactions) == 1

    assert transactions[0].user == user
    assert transactions[0].amount == after_fee(after_ton_network_fee(3.25))
    assert transactions[0].reason == TransactionReason.PREMIUM
    assert transactions[0].recipient == "MySuperCoolFakeRecipient"
