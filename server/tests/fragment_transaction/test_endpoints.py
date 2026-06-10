import pytest
from httpx import AsyncClient

from src.kit.utils import utc_now


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


@pytest.mark.asyncio
@pytest.mark.auth
async def test_get_chart_data(client: AsyncClient) -> None:
    response = await client.get("/v1/transactions/chart")
    assert response.status_code == 200

    json = response.json()

    assert isinstance(json, list)
    assert len(json) == 90

    # given fragment_transaction.created_at is like local
    assert json[-1]["starsTransactionsCount"] == 1
    assert json[-1]["premiumTransactionsCount"] == 1
    assert json[-1]["date"] == utc_now().date().isoformat()
