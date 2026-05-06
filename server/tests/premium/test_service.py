from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.enums import PremiumMonths
from src.exceptions import (
    ResourceNotFound,
)
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.types import (
    BuyLink,
    BuyRequest,
)
from src.premium.service import premium as premium_service
from tests.fixtures.random_objects import (
    get_fake_recipient_data,
    get_valid_transaction,
    rstr,
)


@pytest.mark.asyncio
async def test_gets_right_transaction(fragment_rest: MagicMock) -> None:
    transaction = get_valid_transaction(amount=20)
    fragment_rest.search_premium_gift_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_gift_premium_request.return_value = BuyRequest(
        req_id="", myself=False, amount=0
    )
    fragment_rest.get_gift_premium_link.return_value = BuyLink(
        ok=True,
        transaction=transaction,
    )

    result = await premium_service.get_buy_tc_transaction(
        fragment_rest=fragment_rest,
        username=rstr("username"),
        months=PremiumMonths.SIX_MONTHS,
    )

    fragment_rest.search_premium_gift_recipient.assert_called_once()
    fragment_rest.init_gift_premium_request.assert_called_once()
    fragment_rest.get_gift_premium_link.assert_called_once()

    assert result == transaction


@pytest.mark.asyncio
async def test_get_buy_tc_calls_get_recipient_with_right_data(
    fragment_rest: MagicMock, mocker: MockerFixture
) -> None:
    spy = mocker.spy(premium_service, "get_recipient")

    fragment_rest.search_premium_gift_recipient.return_value = get_fake_recipient_data()

    await premium_service.get_buy_tc_transaction(
        fragment_rest, username="abracadabra", months=PremiumMonths.THREE_MONTHS
    )

    spy.assert_called_once_with(
        fragment_rest=fragment_rest,
        username="abracadabra",
        months=PremiumMonths.THREE_MONTHS,
    )


@pytest.mark.asyncio
async def test_get_recipient_raises_resource_not_found(
    fragment_rest: MagicMock,
) -> None:
    fragment_rest.search_premium_gift_recipient.side_effect = FragmentAPIUsersNotFound()

    with pytest.raises(ResourceNotFound):
        await premium_service.get_recipient(
            fragment_rest, username="cicarro", months=PremiumMonths.THREE_MONTHS
        )
