from unittest.mock import MagicMock

import pytest

from src.enums import PremiumMonths
from src.exceptions import (
    ResourceNotFound,
)
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.types import (
    BuyLink,
    BuyRequest,
)
from src.premium.schemas import PremiumRecipient
from src.premium.service import premium as premium_service
from tests.fixtures.random_objects import (
    get_valid_transaction,
)


@pytest.mark.asyncio
async def test_gets_right_transaction(fragment_rest: MagicMock) -> None:
    transaction = get_valid_transaction(amount=20)
    fragment_rest.init_gift_premium_request.return_value = BuyRequest(
        req_id="", myself=False, amount=0
    )
    fragment_rest.get_gift_premium_link.return_value = BuyLink(
        ok=True,
        transaction=transaction,
    )

    result = await premium_service.get_buy_tc_transaction(
        fragment_rest=fragment_rest,
        recipient_data=PremiumRecipient(recipient="abc", photo="", name=""),
        months=PremiumMonths.SIX_MONTHS,
    )

    fragment_rest.init_gift_premium_request.assert_called_once()
    fragment_rest.get_gift_premium_link.assert_called_once()

    assert result == transaction


@pytest.mark.asyncio
async def test_get_recipient_raises_resource_not_found(
    fragment_rest: MagicMock,
) -> None:
    fragment_rest.search_premium_gift_recipient.side_effect = FragmentAPIUsersNotFound()

    with pytest.raises(ResourceNotFound):
        await premium_service.get_recipient(
            fragment_rest, username="cicarro", months=PremiumMonths.THREE_MONTHS
        )
