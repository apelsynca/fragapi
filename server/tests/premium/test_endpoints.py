from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from src.fragment.types import BuyLink, FoundRecipientData, RecipientData
from src.models import User
from tests.fixtures.random_objects import get_valid_transaction


@pytest.mark.asyncio
async def test_rejects_get_recipient_without_auth(client: AsyncClient) -> None:
    response = await client.get("/v1/premium/recipient/homocitrus")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
async def test_buy_or_smth(
    client: AsyncClient, fragment: MagicMock, wallet_manager: MagicMock, user: User
) -> None:
    user.balance = 100
    wallet_manager.transfer_from_tc.return_value = "somehashik"
    wallet_manager.get_balance.return_value = 100

    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(myself=False, recipient="ogurchik", photo="", name=""),
    )
    fragment.get_gift_premium_link.return_value = BuyLink(
        ok=True, transaction=get_valid_transaction(amount=5)
    )

    response = await client.post(
        "/v1/premium/buy", json={"username": "ogurchik", "months": "12"}
    )

    assert response.status_code == 200

    json = response.json()

    assert json["messageHash"] == "somehashik"
