import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_requires_non_anon(client: AsyncClient) -> None:
    response = await client.get("/v1/panel/fragment/rate")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
async def test_gets_ton_rate(client: AsyncClient) -> None:
    response = await client.get("/v1/panel/fragment/rate")
    assert response.status_code == 200
    json = response.json()

    assert "tonRate" in json
