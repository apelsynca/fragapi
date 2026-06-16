import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_openapi(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()

    assert schema["info"]["title"] == "FragAPI"
    assert "tags" in schema
