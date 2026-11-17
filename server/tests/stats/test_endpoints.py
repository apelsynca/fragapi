import pytest
from httpx import AsyncClient

from src.kit.utils import utc_now
from src.models import Transaction, User
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction, create_transaction


async def create_purchase(
    save_fixture: SaveFixture,
    user: User,
    *,
    stars_amount: int | None = None,
    premium_months: int | None = None,
    sent: bool = True,
) -> Transaction:
    transaction = await create_transaction(
        save_fixture,
        user=user,
        ton_transaction=await create_ton_transaction(save_fixture),
        stars_amount=stars_amount,
        premium_months=premium_months,
    )
    if sent:
        transaction.sent_at = utc_now()
        await save_fixture(transaction)

    return transaction


@pytest.mark.asyncio
async def test_totals_are_public_and_zero_without_purchases(
    client: AsyncClient,
) -> None:
    response = await client.get("/v1/stats/totals")

    assert response.status_code == 200
    assert response.json() == {"starsTotal": 0, "premiumMonthsTotal": 0}


@pytest.mark.asyncio
async def test_totals_sum_stars_and_premium_months_separately(
    client: AsyncClient, save_fixture: SaveFixture, user: User
) -> None:
    await create_purchase(save_fixture, user, stars_amount=50)
    await create_purchase(save_fixture, user, stars_amount=1000)
    await create_purchase(save_fixture, user, premium_months=3)
    await create_purchase(save_fixture, user, premium_months=12)

    response = await client.get("/v1/stats/totals")

    assert response.json() == {"starsTotal": 1050, "premiumMonthsTotal": 15}


@pytest.mark.asyncio
async def test_totals_skip_purchases_that_were_not_sent(
    client: AsyncClient, save_fixture: SaveFixture, user: User
) -> None:
    await create_purchase(save_fixture, user, stars_amount=50)
    await create_purchase(save_fixture, user, stars_amount=500, sent=False)
    await create_purchase(save_fixture, user, premium_months=6, sent=False)

    response = await client.get("/v1/stats/totals")

    assert response.json() == {"starsTotal": 50, "premiumMonthsTotal": 0}


@pytest.mark.asyncio
async def test_totals_are_cached(
    client: AsyncClient, save_fixture: SaveFixture, user: User
) -> None:
    await create_purchase(save_fixture, user, stars_amount=50)
    first = await client.get("/v1/stats/totals")

    await create_purchase(save_fixture, user, stars_amount=100)
    second = await client.get("/v1/stats/totals")

    assert first.json() == second.json() == {"starsTotal": 50, "premiumMonthsTotal": 0}
