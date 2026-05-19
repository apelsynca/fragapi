import pytest
from httpx import AsyncClient
from ton_core import to_nano

from src.config import settings


@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.parametrize("amount", [0.49, 1, 3.22, 1.235, 999, 100])
async def test_ton_payment_right_data(client: AsyncClient, amount: float) -> None:
    response = await client.post("/v1/payments/ton", params={"amount": amount})

    assert response.status_code == 200
    json = response.json()

    assert json["amount"] == str(to_nano(amount))
    assert json["address"] == settings.TON_ADDRESS
    assert "payload" in json
