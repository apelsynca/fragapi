from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from src.tonapi.schemas import TonAPIWebhookMessage
from src.tonapi.service import TonAPIService
from tests.fixtures.random_objects import rstr


@pytest.fixture(autouse=True)
def tonapi_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.tonapi.endpoints.tonapi_service", spec=TonAPIService)


@pytest.mark.asyncio
async def test_tonapi_webhook_silent(
    client: AsyncClient, tonapi_service: MagicMock
) -> None:
    response = await client.post(
        "/v1/tonapi/webhook",
        json={
            "event_type": "random_bullshit",
            "account_id": "someaccountid",
            "lt": 123,
            "tx_hash": rstr("somehash"),
        },
    )
    assert response.status_code == 200

    tonapi_service.process_webhook_account_tx_message.assert_not_called()


@pytest.mark.asyncio
async def test_tonapi_webhook_good(
    client: AsyncClient, tonapi_service: MagicMock
) -> None:
    response = await client.post(
        "/v1/tonapi/webhook",
        json={
            "event_type": "account_tx",
            "account_id": "0:ssssuperaccid",
            "lt": 52020202,
            "tx_hash": "sometx_hashverygood",
        },
    )
    assert response.status_code == 200

    tonapi_service.process_webhook_account_tx_message.assert_called_once_with(
        message=TonAPIWebhookMessage(
            event_type="account_tx",
            account_id="0:ssssuperaccid",
            lt=52020202,
            tx_hash="sometx_hashverygood",
        )
    )
