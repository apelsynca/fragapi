import pytest
from httpx import AsyncClient

from src.kit.utils import utc_now
from src.models import FragmentTransaction


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
async def test_get_chart_data(
    client: AsyncClient, fragment_transaction: FragmentTransaction
) -> None:
    response = await client.get("/v1/transactions/chart")
    assert response.status_code == 200

    json = response.json()

    assert isinstance(json, list)
    assert len(json) == 90

    # given fragment_transaction.created_at is like local
    assert json[-1]["tonAmount"] == fragment_transaction.amount
    assert json[-1]["transactionsCount"] == 1
    assert json[-1]["date"] == utc_now().date().isoformat()
