from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.auth
async def test_get_ton_rate(client: AsyncClient, fragment: MagicMock) -> None:
    response = await client.get("/v1/ton/rate")
    assert response.status_code == 200

    json = response.json()

    assert json["tonRate"] is not None

    fragment.get_ton_usd_rate.assert_called_once()


@pytest.mark.asyncio
async def test_get_ton_rate_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/v1/ton/rate")
    assert response.status_code == 401
