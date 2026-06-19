import pytest
from httpx import AsyncClient
from ton_core import to_nano

from src.config import settings
from src.models import User
from tests.deposit.conftest import create_deposit
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_transaction


@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.parametrize("amount", [0.49, 1, 3.22, 1.235, 999, 100])
async def test_ton_deposit_right_data(client: AsyncClient, amount: float) -> None:
    response = await client.post("/v1/deposits/ton", params={"amount": amount})

    assert response.status_code == 200
    json = response.json()

    assert json["amount"] == str(to_nano(amount))
    assert json["address"] == settings.TON_ADDRESS
    assert "payload" in json


@pytest.mark.asyncio
@pytest.mark.auth
async def test_list_deposits(
    save_fixture: SaveFixture, client: AsyncClient, user: User
) -> None:
    await create_deposit(save_fixture, user=user, amount=5.25, completed=False)
    await create_deposit(save_fixture, user=user, amount=5.25, completed=True)

    response = await client.get("/v1/deposits/")
    assert response.status_code == 200

    json = response.json()

    assert "items" in json
    assert "pagination" in json

    assert len(json["items"]) == 1
    item = json["items"][0]

    assert item["amount"] == 5.25
    assert item["createdAt"] is not None
    assert item["status"] == "completed"
    assert item["transaction"] is None


@pytest.mark.asyncio
@pytest.mark.auth
async def test_list_deposits_also_gives_tx_hash_if_present(
    save_fixture: SaveFixture, user: User, client: AsyncClient
) -> None:
    transaction = await create_transaction(save_fixture, amount=5.25, hash="MyTxHash")
    await create_deposit(
        save_fixture, user=user, amount=5.25, transaction=transaction, completed=True
    )

    response = await client.get("/v1/deposits/")
    assert response.status_code == 200

    json = response.json()

    item = json["items"][0]

    assert item["transaction"]["hash"] == "MyTxHash"
    assert item["status"] == "completed"
