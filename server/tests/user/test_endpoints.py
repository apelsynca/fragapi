import pytest
from httpx import AsyncClient

from src.auth.scope import Scope
from tests.fixtures.auth import AuthSubjectFixture


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


@pytest.mark.asyncio
@pytest.mark.auth(AuthSubjectFixture(subject="user", scopes={Scope.read_api_keys}))
async def test_gets_api_keys(client: AsyncClient):
    response = await client.get("/v1/users/api-keys")
    assert response.status_code == 200

    json = response.json()

    assert isinstance(json, list)
    assert len(json) == 0


@pytest.mark.asyncio
@pytest.mark.auth(
    AuthSubjectFixture(subject="user", scopes=set(Scope) - {Scope.read_api_keys})
)
async def test_gets_api_keys_requires_scope(client: AsyncClient) -> None:
    response = await client.get("/v1/users/api-keys")
    assert response.status_code == 401
