from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pydantic import ValidationError
from pytest_mock import MockerFixture

from src.models import User
from src.stars.service import StarsService


@pytest.fixture(autouse=True)
def stars_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.stars.endpoints.stars_service", spec=StarsService)


@pytest.mark.asyncio
@pytest.mark.auth
async def test_gets_stars(
    client: AsyncClient, user: User, stars_service_mock: MagicMock
) -> None:
    stars_service_mock.buy.return_value = "some-transhash"

    response = await client.post(
        "/v1/stars/buy", json={"quantity": 50, "username": "Nishonov"}
    )
    assert response.status_code == 200
    json = response.json()

    assert json["success"] is True
    assert json["transactionHash"] == "some-transhash"

    stars_service_mock.buy.assert_called_once_with(
        user=user, quantity=50, username="Nishonov"
    )


@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.parametrize("quantity", [49, 1, -200, 25])
async def test_error_if_less_than_50(client: AsyncClient, quantity: int) -> None:
    with pytest.raises(ValidationError):
        await client.post(
            "/v1/stars/buy", json={"quantity": quantity, "username": "someusername"}
        )


@pytest.mark.asyncio
async def test_get_price():
    pass
