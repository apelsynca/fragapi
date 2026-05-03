import pytest
from httpx import AsyncClient

from src.models import User


@pytest.mark.asyncio
async def test_not_found(client: AsyncClient, user: User) -> None:
    response = await client.get(
        "/v1/gifts/plushpepe/short-models",
        headers={"Authorization": f"Bearer {user.api_key}"},
    )
    assert response.status_code == 200

    response = await client.get(
        "/v1/gifts/someothernonexistent/short-models",
        headers={"Authorization": f"Bearer {user.api_key}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_all_lowercased(client: AsyncClient, user: User) -> None:
    response = await client.get(
        "/v1/gifts/plushpepe/short-models",
        headers={"Authorization": f"Bearer {user.api_key}"},
    )
    assert response.status_code == 200

    json = response.json()

    for item in json:
        assert isinstance(item, str)
        assert item.islower()
