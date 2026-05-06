from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.exceptions import BadRequest
from src.fragment_rest.rest import FragmentRest
from src.fragment_rest.types import BuyLink, BuyRequest
from src.stars.service import stars as stars_service
from tests.fixtures.random_objects import get_fake_recipient_data, get_valid_transaction


@pytest.mark.asyncio
async def test_get_buy_tc_calls_get_recipient_with_quantity(
    fragment_rest: MagicMock,
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(stars_service, "get_recipient")

    transaction = get_valid_transaction(amount=2.2)
    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id="", myself=False, amount=0
    )
    fragment_rest.get_buy_stars_link.return_value = BuyLink(
        ok=True,
        transaction=transaction,
    )

    ton_connect_transaction = await stars_service.get_tc_transaction(
        fragment_rest=fragment_rest,
        username="abobus",
        quantity=1337,
    )

    fragment_rest.search_stars_recipient.assert_called_once()
    fragment_rest.init_buy_stars_request.assert_called_once()
    fragment_rest.get_buy_stars_link.assert_called_once()

    assert ton_connect_transaction == transaction

    spy.assert_called_once_with(
        fragment_rest=fragment_rest, username="abobus", quantity=1337
    )


@pytest.mark.asyncio
async def test_get_buy_transaction(fragment_rest: MagicMock) -> None:
    transaction = get_valid_transaction(amount=2.2)
    fragment_rest.search_stars_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_buy_stars_request.return_value = BuyRequest(
        req_id="", myself=False, amount=0
    )
    fragment_rest.get_buy_stars_link.return_value = BuyLink(
        ok=True,
        transaction=transaction,
    )

    ton_connect_transaction = await stars_service.get_tc_transaction(
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
    # i know here maybe FragRequestValidationError is better
    with pytest.raises(BadRequest):
        await stars_service.get_tc_transaction(
            fragment_rest=fragment_rest,
            username="someusername",
            quantity=quantity,
        )
