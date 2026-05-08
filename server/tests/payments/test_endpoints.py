import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_ton_payment_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/v1/payments/ton", params={"amount": 5})
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
async def test_request_ton_payment(client: AsyncClient) -> None:
    response = await client.get("/v1/payments/ton", params={"amount": 5})
    assert response.status_code == 200

    json = response.json()

    assert "address" in json
