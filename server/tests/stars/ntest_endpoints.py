from unittest.mock import ANY

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.stars.schemas import BuyStarsResponse, StarsRecipient
from tests.fixtures.random_objects import get_valid_tc_transaction


@pytest.mark.asyncio
async def test_rejects_get_recipient_without_auth(client: AsyncClient) -> None:
    response = await client.get("/v1/stars/recipient/homocitrus")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
async def test_buy_makes_right_callls_buy_from_tc(
    client: AsyncClient, mocker: MockerFixture, session: AsyncSession, user: User
) -> None:
    # i know its bad
    tc_transaction = get_valid_tc_transaction(amount=2.225)
    mocker.patch(
        "src.stars.endpoints.stars_service.get_recipient",
        return_value=StarsRecipient(recipient="abobus", photo="", name=""),
    )
    mocker.patch(
        "src.stars.endpoints.stars_service.get_tc_transaction",
        return_value=tc_transaction,
    )
    mock = mocker.patch(
        "src.stars.endpoints.stars_service.buy_from_tc_transaction",
        return_value=BuyStarsResponse(message_hash="any"),
    )

    response = await client.post(
        "/v1/stars/buy", json={"quantity": 50, "username": "susybaka"}
    )
    assert response.status_code == 200

    mock.assert_called_once_with(
        session=session,
        user=user,
        wallet_manager=ANY,
        tc_transaction=tc_transaction,
        recipient="abobus",
    )
