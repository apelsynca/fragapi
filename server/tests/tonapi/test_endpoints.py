import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_response_200_even_if_wrong_event_type(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/tonapi/webhook",
        json={
            "event_type": "account_tx",
            "account_id": "xxx-xxx-xxx",
            "lt": 99999,
            "tx_hash": "",
        },
    )

    assert response.status_code == 200
