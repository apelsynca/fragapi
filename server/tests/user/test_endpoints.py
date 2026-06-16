import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_requires_auth_duhh(client: AsyncClient) -> None:
    response = await client.get("/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
async def test_gets_user(client: AsyncClient) -> None:
    response = await client.get("/v1/users/me")
    assert response.status_code == 200

    json = response.json()

    assert "balance" in json
    assert "firstName" in json
    assert "lastName" in json
    assert "username" in json
