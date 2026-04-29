from unittest.mock import MagicMock

import pytest

from src.exceptions import AppError
from src.thermos.schemas import GiftModel
from src.thermos.service import thermos as thermos_service
from tests.thermos.conftest import (
    generate_fake_collection_response,
    generate_fake_gift_coll,
)


@pytest.mark.asyncio
async def test_ignores_dashes(thermos_proxy_mock: MagicMock) -> None:
    thermos_proxy_mock.get_collections.return_value = [
        generate_fake_gift_coll("Does-Not-Matter"),
        generate_fake_gift_coll("Rick And Morty"),
    ]
    thermos_proxy_mock.get_collection.return_value = generate_fake_collection_response(
        "Does-Not-Matter",
        {"Silver": 2200000000, "Gold": 1750000000, "Other Random-Stuff": 3250000000},
    )

    model = await thermos_service.find_collection_model(
        short_name="doesnotmatter", model="silver"
    )
    assert model == GiftModel(
        name="silver", floor=2.2, count=1, image_url=model.image_url
    )


@pytest.mark.asyncio
async def test_ignores_spaces(thermos_proxy_mock: MagicMock) -> None:
    thermos_proxy_mock.get_collections.return_value = [
        generate_fake_gift_coll("Jack In The Basket"),
        generate_fake_gift_coll("Pliny the-Elder"),
    ]
    thermos_proxy_mock.get_collection.return_value = generate_fake_collection_response(
        "Jack In The Basket",
        {"Laimon Fresh": 9919000000, "Apple": 1750000000, "Kozaborka": 3250000000},
    )

    model = await thermos_service.find_collection_model(
        short_name="jackinthebasket", model="laimonfresh"
    )
    assert model == GiftModel(
        name="laimonfresh", floor=9.919, count=1, image_url=model.image_url
    )


@pytest.mark.asyncio
async def test_raises_if_not_found_coll(thermos_proxy_mock: MagicMock) -> None:
    thermos_proxy_mock.get_collections.return_value = [
        generate_fake_gift_coll("Jack In The Basket"),
        generate_fake_gift_coll("Aristotel"),
    ]
    thermos_proxy_mock.get_collection.return_value = generate_fake_collection_response(
        "Jack In The Basket",
        {"Laimon Fresh": 9919000000, "Apple": 1750000000, "Kozaborka": 3250000000},
    )

    with pytest.raises(AppError):
        await thermos_service.find_collection_model(
            short_name="someother", model="laimonfresh"
        )


@pytest.mark.asyncio
async def test_raises_if_not_found_model(thermos_proxy_mock: MagicMock) -> None:
    thermos_proxy_mock.get_collections.return_value = [
        generate_fake_gift_coll("someother"),
        generate_fake_gift_coll("bunny"),
    ]
    thermos_proxy_mock.get_collection.return_value = generate_fake_collection_response(
        "bunny",
        {"Laimon Fresh": 9919000000, "Apple": 1750000000, "Kozaborka": 3250000000},
    )

    with pytest.raises(AppError):
        await thermos_service.find_collection_model(
            short_name="bunny", model="limonsoft"
        )
