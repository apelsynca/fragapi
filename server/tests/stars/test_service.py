from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.exceptions import BadRequest, FragError, InsuficcientFunds, ResourceNotFound
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.types import BuyLink, BuyRequest
from src.models import User
from src.stars.service import stars as stars_service
from src.wallet.types import TonConnectMessage, TonConnectTransaction
from tests.fixtures.random_objects import get_fake_recipient_data, rstr


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [49, 1, -200, 10_000_001])
async def test_raises_bad_request_if_invalid_quantity(
    session: AsyncSession,
    fragment_rest: MagicMock,
    wallet_manager: MagicMock,
    user: User,
    quantity: int,
) -> None:
    with pytest.raises(BadRequest):
        await stars_service.buy(
            session=session,
            fragment_rest=fragment_rest,
            wallet_manager=wallet_manager,
            user_id=user.id,
            username="",
            quantity=quantity,
        )


@pytest.mark.asyncio
async def test_get_recipient_raises_when_not_found(fragment_rest: MagicMock) -> None:
    fragment_rest.search_stars_recipient.side_effect = FragmentAPIUsersNotFound

    with pytest.raises(ResourceNotFound):
        await stars_service.get_recipient(fragment_rest, username="googooga")

    fragment_rest.search_stars_recipient.assert_called_once_with(
        query="googooga", quantity=ANY
    )


@pytest.mark.asyncio
async def test_buy_raises_if_not_enough_balance(
    session: AsyncSession,
    fragment_rest: MagicMock,
    wallet_manager: MagicMock,
    user: User,
) -> None:
    assert user.balance == 0

    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id=rstr("someid"), myself=False, amount=52.291
    )

    with pytest.raises(InsuficcientFunds):
        await stars_service.buy(
            session=session,
            fragment_rest=fragment_rest,
            wallet_manager=wallet_manager,
            user_id=user.id,
            username="homocitrus",
            quantity=50,
        )


@pytest.mark.asyncio
async def test_buy_raises_not_enough_balance_if_same_amount(
    session: AsyncSession,
    fragment_rest: MagicMock,
    wallet_manager: MagicMock,
    user: User,
) -> None:
    assert settings.API_PRICE_MARKUP != 0

    user.balance = 123.52

    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id=rstr("someid"), myself=False, amount=123.52
    )

    with pytest.raises(InsuficcientFunds):
        await stars_service.buy(
            session=session,
            fragment_rest=fragment_rest,
            wallet_manager=wallet_manager,
            user_id=user.id,
            username="doesnotmatter",
            quantity=52,
        )


@pytest.mark.asyncio
async def test_buy_raises_if_user_not_found(
    session: AsyncSession, fragment_rest: MagicMock, wallet_manager: MagicMock
) -> None:
    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id=rstr("someid"), myself=False, amount=123.52
    )

    with pytest.raises(FragError):
        await stars_service.buy(
            session=session,
            fragment_rest=fragment_rest,
            wallet_manager=wallet_manager,
            user_id=291529,
            username="doesnotmatter",
            quantity=52,
        )


@pytest.mark.asyncio
async def test_raises_app_error_if_wallet_balance_is_lower(
    session: AsyncSession,
    user: User,
    wallet_manager: MagicMock,
    fragment_rest: MagicMock,
) -> None:
    wallet_manager.get_balance.return_value = 5
    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id=rstr("something"), myself=False, amount=5.25
    )
    fragment_rest.get_buy_stars_link.return_value = BuyLink(
        ok=True,
        transaction=TonConnectTransaction(
            valid_until=datetime(year=2000, month=2, day=3),
            from_address="SomeAddressFrom",
            messages=[TonConnectMessage(address="", amount=0, payload=None)],
        ),
    )

    user.balance = 100

    with pytest.raises(FragError):
        await stars_service.buy(
            session=session,
            fragment_rest=fragment_rest,
            wallet_manager=wallet_manager,
            user_id=user.id,
            username="anything",
            quantity=250,
        )


@pytest.mark.asyncio
async def test_caches_star_price() -> None:
    await stars_service.get_single_star_price()


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [49, 1, -200, 10_000_001])
async def test_get_stars_price_raises_invalid_quantity(quantity: int) -> None:
    with pytest.raises(BadRequest):
        await stars_service.get_price(quantity=quantity)
