from unittest.mock import MagicMock

import pytest

from src.exceptions import BadRequest
from src.fragment.types import BuyLink, BuyRequest
from src.stars.schemas import StarsRecipient
from src.stars.service import stars as stars_service
from tests.fixtures.random_objects import get_valid_tc_transaction


@pytest.mark.asyncio
async def test_get_buy_transaction(fragment: MagicMock) -> None:
    transaction = get_valid_tc_transaction(amount=2.2)
    fragment.init_buy_stars_request.return_value = BuyRequest(
        req_id="", myself=False, amount=0
    )
    fragment.get_buy_stars_link.return_value = BuyLink(
        ok=True,
        transaction=transaction,
    )

    ton_connect_transaction = await stars_service.get_tc_transaction(
        fragment=fragment,
        recipient_data=StarsRecipient(recipient="abc", photo="", name=""),
        quantity=50,
    )

    fragment.init_buy_stars_request.assert_called_once()
    fragment.get_buy_stars_link.assert_called_once()

    assert ton_connect_transaction == transaction


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [49, 1, -200, 10_000_001])
async def test_get_buy_trans_raises_on_invalid_quantity(
    fragment: MagicMock, quantity: int
) -> None:
    # i know here maybe FragRequestValidationError is better
    with pytest.raises(BadRequest):
        await stars_service.get_tc_transaction(
            fragment=fragment,
            recipient_data=StarsRecipient(recipient="somerecipient", photo="", name=""),
            quantity=quantity,
        )
