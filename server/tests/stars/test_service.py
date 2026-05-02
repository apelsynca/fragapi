from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.exceptions import InsuficcientFunds, ResourceNotFound
from src.fragment_rest.exceptions import FragmentBadRequest
from src.fragment_rest.main import FragmentRest
from src.fragment_rest.types import BuyStarsRequest, FragmentRecipient, RecipientFound
from src.models import User
from src.stars.service import stars as stars_service
from tests.fixtures.random_objects import rstr


@pytest.fixture(autouse=True)
def fragment_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.stars.service.fragment_rest", spec=FragmentRest)


@pytest.mark.asyncio
async def test_get_recipient_not_found_fragment_bad_request(
    fragment_mock: MagicMock,
) -> None:
    fragment_mock.search_stars_recipient.side_effect = FragmentUsersNotFound()

    with pytest.raises(ResourceNotFound):
        await stars_service.get_recipient(username="apelsynca")


@pytest.mark.asyncio
async def test_buy_gets_buy_stars_link() -> None:
    pass


@pytest.mark.asyncio
async def test_buy_for_nonexistent_username(
    user: User, fragment_mock: MagicMock
) -> None:
    fragment_mock.search_stars_recipient.side_effect = FragmentBadRequest(
        "No Telegram users found."
    )

    with pytest.raises(ResourceNotFound):
        await stars_service.buy(user, quantity=52, username="abrikos")


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [49, -200])
async def test_buy_quantity_less_50(user: User, quantity: int, username: str) -> None:
    with pytest.raises(FragValidationError):
        await stars_service.buy(user, quantity, username)


@pytest.mark.asyncio
@pytest.mark.parametrize("amount", [0, 5, 200])
async def test_buy_balance_less_than_price(
    user: User, fragment_mock: MagicMock, amount: float
) -> None:
    assert user.balance == 0

    fragment_mock.search_stars_recipient.return_value = FragmentRecipient(
        ok=True,
        found=RecipientFound(myself=False, recipient="abc", photo="abc", name="abc"),
    )
    fragment_mock.init_buy_stars_request.return_value = BuyStarsRequest(
        req_id=rstr("reqid"), myself=False, amount=amount, to_bot=False
    )

    with pytest.raises(InsuficcientFunds):
        await stars_service.buy(user, quantity=50, username="abrakacadra")
