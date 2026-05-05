from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.exceptions import BadRequest, FragError, InsuficcientFunds, ResourceNotFound
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.types import BuyLink, BuyRequest
from src.models import User
from src.stars.service import stars as stars_service
from src.wallet.service import WalletService
from src.wallet.types import TonConnectMessage, TonConnectTransaction
from tests.fixtures.random_objects import get_fake_recipient_data, rstr


@pytest.fixture(autouse=True)
def wallet_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.stars.service.wallet_service", spec=WalletService)


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [49, 1, -200, 10_000_001])
async def test_raises_bad_request_if_invalid_quantity(
    session: AsyncSession, user: User, quantity: int, fragment_rest: MagicMock
) -> None:
    with pytest.raises(BadRequest):
        await stars_service.buy(
            session, fragment_rest, user_id=user.id, username="", quantity=quantity
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
    session: AsyncSession, user: User, fragment_rest: MagicMock
) -> None:
    assert user.balance == 0

    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id=rstr("someid"), myself=False, amount=52.291
    )

    with pytest.raises(InsuficcientFunds):
        await stars_service.buy(
            session, fragment_rest, user_id=user.id, username="homocitrus", quantity=50
        )


@pytest.mark.asyncio
async def test_buy_raises_not_enough_balance_if_same_amount(
    session: AsyncSession, user: User, fragment_rest: MagicMock
) -> None:
    assert settings.API_PRICE_MARKUP != 0

    user.balance = 123.52

    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id=rstr("someid"), myself=False, amount=123.52
    )

    with pytest.raises(InsuficcientFunds):
        await stars_service.buy(
            session,
            fragment_rest,
            user_id=user.id,
            username="doesnotmatter",
            quantity=52,
        )


@pytest.mark.asyncio
async def test_buy_raises_if_user_not_found(
    session: AsyncSession, fragment_rest: MagicMock
) -> None:
    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id=rstr("someid"), myself=False, amount=123.52
    )

    with pytest.raises(FragError):
        await stars_service.buy(
            session,
            fragment_rest,
            user_id=291529,
            username="doesnotmatter",
            quantity=52,
        )


@pytest.mark.asyncio
async def test_calls_get_wallet_balance(
    session: AsyncSession,
    fragment_rest: MagicMock,
    user: User,
    wallet_service: MagicMock,
) -> None:
    wallet_service.get_balance.return_value = 100
    wallet_service.transfer_from_tc.return_value = "xxx-somehash-KAKA"
    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id=rstr("something"), myself=False, amount=2.82
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

    buy_stars_response = await stars_service.buy(
        session, fragment_rest, user_id=user.id, username="random", quantity=52
    )

    wallet_service.get_balance.assert_called_once()

    assert buy_stars_response.transaction_hash == "xxx-somehash-KAKA"


@pytest.mark.asyncio
async def test_raises_app_error_if_wallet_balance_is_lower(
    session: AsyncSession,
    user: User,
    fragment_rest: MagicMock,
    wallet_service: MagicMock,
) -> None:
    wallet_service.get_balance.return_value = 5
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
            session, fragment_rest, user_id=user.id, username="anything", quantity=250
        )


@pytest.mark.asyncio
async def test_caches_star_price() -> None:
    await stars_service.get_single_star_price()


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [49, 1, -200, 10_000_001])
async def test_get_stars_price_raises_invalid_quantity(quantity: int) -> None:
    with pytest.raises(BadRequest):
        await stars_service.get_price(quantity=quantity)
