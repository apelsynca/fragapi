from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_nano

from src.config import settings
from src.exceptions import (
    BadRequest,
    FragError,
    FragRequestValidationError,
    InsuficcientFunds,
)
from src.fee import TON_FEE
from src.fragment_rest.rest import FragmentRest
from src.fragment_rest.types import (
    BuyLink,
    BuyRequest,
    FoundRecipientData,
    RecipientData,
)
from src.models.users import User
from src.stars.service import stars as stars_service
from src.wallet.types import TonConnectMessage
from tests.fixtures.random_objects import (
    get_tc_transaction,
    get_valid_transaction,
    rstr,
)


@pytest.mark.asyncio
async def test_get_buy_transaction(fragment_rest: MagicMock) -> None:
    transaction = get_valid_transaction(amount=2.2)
    fragment_rest.search_stars_recipient.return_value = RecipientData(
        ok=True, found=FoundRecipientData(myself=False, recipient="", photo="", name="")
    )
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id="", myself=False, amount=0
    )
    fragment_rest.get_buy_stars_link.return_value = BuyLink(
        ok=True,
        transaction=transaction,
    )

    ton_connect_transaction = await stars_service.get_buy_tc_transaction(
        fragment_rest=fragment_rest,
        username="someusername",
        quantity=50,
    )

    fragment_rest.search_stars_recipient.assert_called_once()
    fragment_rest.init_buy_stars_request.assert_called_once()
    fragment_rest.get_buy_stars_link.assert_called_once()

    assert ton_connect_transaction == transaction


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [49, 1, -200, 10_000_001])
async def test_get_buy_trans_raises_on_invalid_quantity(
    fragment_rest: FragmentRest, quantity: int
) -> None:
    with pytest.raises(BadRequest):
        await stars_service.get_buy_tc_transaction(
            fragment_rest=fragment_rest,
            username="someusername",
            quantity=quantity,
        )


@pytest.mark.asyncio
async def test_buy_from_transaction_calls_wallet_manager_right(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    user.balance = 50
    tc_transaction = get_valid_transaction(1)
    wallet_manager.get_balance.return_value = 50
    wallet_manager.transfer_from_tc.return_value = "WHATTHEHELLY"

    message_hash = await stars_service.buy_from_transaction(
        session=session,
        user=user,
        wallet_manager=wallet_manager,
        transaction=tc_transaction,
    )

    wallet_manager.transfer_from_tc.assert_called_once_with(transaction=tc_transaction)
    assert user.balance < 50
    assert message_hash == "WHATTHEHELLY"


@pytest.mark.asyncio
async def test_buy_from_transa_raises_if_insufficient_funds(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    assert user.balance == 0
    wallet_manager.get_balance.return_value = 50
    tc_transaction = get_valid_transaction(1.1)

    with pytest.raises(InsuficcientFunds):
        await stars_service.buy_from_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=tc_transaction,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_buy_from_transaction_raises_if_wallet_balance_lower(
    session: AsyncSession,
    user: User,
    wallet_manager: MagicMock,
) -> None:
    user.balance = 1000.251
    wallet_manager.get_balance.return_value = 5.25
    transaction = get_valid_transaction(amount=25.25)

    with pytest.raises(FragError):
        await stars_service.buy_from_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=transaction,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_buy_from_transaction_raises_if_no_message(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    user.balance = 50
    transa = get_tc_transaction(messages=[])

    with pytest.raises(FragRequestValidationError):
        await stars_service.buy_from_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=transa,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_buy_from_transaction_raises_if_more_than_one_message(
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
        await stars_service.buy_from_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=transa,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_buy_from_transaction_raises_if_payload_is_none(
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
        await stars_service.buy_from_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=transa,
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

    await stars_service.buy_from_transaction(
        session=session,
        user=user,
        wallet_manager=wallet_manager,
        transaction=transaction,
    )

    price = 2.5 + (2.5 * settings.API_PRICE_MARKUP) + TON_FEE

    # 10.25 - 2.5 ...
    assert user.balance == 10.25 - price
    wallet_manager.transfer_from_tc.assert_called_once()


@pytest.mark.asyncio
async def test_buy_raises_despite_fee(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    settings.API_PRICE_MARKUP = 0.25  # 25%

    user.balance = 11.3
    transaction = get_valid_transaction(amount=11.3)
    wallet_manager.get_balance.return_value = 11.31

    with pytest.raises(InsuficcientFunds):
        await stars_service.buy_from_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=transaction,
        )

    wallet_manager.transfer_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_buy_raises_frag_error_if_wallet_balance_plus_fee(
    session: AsyncSession, user: User, wallet_manager: MagicMock
) -> None:
    settings.API_PRICE_MARKUP = 0

    user.balance = 11.3
    transaction = get_valid_transaction(amount=11.3)
    # still lower
    wallet_manager.get_balance.return_value = 11.29998 + TON_FEE

    with pytest.raises(FragError):
        await stars_service.buy_from_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=transaction,
        )

    wallet_manager.transfer_from_tc.assert_not_called()
