import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rejects_get_recipient_without_auth(client: AsyncClient) -> None:
    response = await client.get("/v1/premium/recipient/homocitrus")
    assert response.status_code == 401
