import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gets_stats_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/v1/transactions/stats")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
async def test_gets_stats(client: AsyncClient) -> None:
    response = await client.get("/v1/transactions/stats")
    assert response.status_code == 200

    json = response.json()

    assert "totalSpend" in json
    assert "starsTotalSpend" in json
    assert "premiumTotalSpend" in json
