from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.kit.utils import utc_now
from src.models import ApiToken, User
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_api_token


@pytest.mark.asyncio
async def test_get_all_tokens_requires_auth(client: AsyncClient) -> None:
    response = await client.get(url="/v1/api-tokens")

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
async def test_get_all_tokens_valid_data(
    save_fixture: SaveFixture, client: AsyncClient, user: User
) -> None:
    await create_api_token(save_fixture, user=user, name="The name")

    response = await client.get(url="/v1/api-tokens")

    assert response.status_code == 200
    json = response.json()

    assert len(json) == 1
    assert json[0]["name"] == "The name"
    assert json[0]["token"] is not None
    assert json[0]["lastUsedAt"] is None


@pytest.mark.asyncio
@pytest.mark.auth
async def test_create_token(client: AsyncClient) -> None:
    response = await client.post("/v1/api-tokens", json={"name": "myname"})

    assert response.status_code == 200
    json = response.json()

    assert json["name"] == "myname"
    assert json["token"] is not None
    assert json["expiresAt"] is None
    assert json["lastUsedAt"] is None


@pytest.mark.asyncio
@pytest.mark.auth
async def test_create_token_expires_at(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/api-tokens",
        json={
            "name": "myname",
            "expiresAt": int((utc_now() + timedelta(days=5)).timestamp()),
        },
    )

    assert response.status_code == 200
    json = response.json()

    assert json["expiresAt"] is not None
    assert json["lastUsedAt"] is None


@pytest.mark.asyncio
@pytest.mark.auth
async def test_delete_token(
    client: AsyncClient, save_fixture: SaveFixture, user: User, session: AsyncSession
) -> None:
    api_token = await create_api_token(save_fixture, user=user)

    response = await client.delete(f"/v1/api-tokens/{api_token.id}")

    assert response.status_code == 200

    api_token = await session.scalar(select(ApiToken).where(ApiToken.user == user))
    assert api_token is None
