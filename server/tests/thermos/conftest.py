import random
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.thermos.proxy_api import ThermosProxyAPI
from src.thermos.types import (
    AggregatedStats,
    GetCollectionResponse,
    GiftCollection,
    GiftCollectionAttributes,
    ThermosGiftModel,
)
from tests.fixtures.random_objects import rstr


def generate_fake_gift_coll(collection_name: str) -> GiftCollection:
    return GiftCollection(
        name=collection_name,
        image_url="https://example.com/image.jpg",
        stats=AggregatedStats(count=2, floor=1.25),
        id=rstr("theid"),
    )


def generate_fake_collection_response(
    collection_name: str, gift_models: dict[str, float] = {}
) -> GetCollectionResponse:
    return GetCollectionResponse(
        collection=generate_fake_gift_coll(collection_name),
        attributes=GiftCollectionAttributes(
            models=[
                ThermosGiftModel(
                    name=gift_model,
                    rarity_per_mille=random.randint(10, 70),
                    image_url="https://example.com/image.jpg",
                    stats=AggregatedStats(count=1, floor=floor),
                )
                for (gift_model, floor) in gift_models.items()
            ],
            backdrops=[],
            symbols=[],
        ),
    )


@pytest.fixture(autouse=True)
def thermos_proxy_mock(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("src.thermos.service.thermos.api", spec=ThermosProxyAPI)
    # thermos_proxy_mock.get_collection_model = ThermosGiftModel(
    #     name="Silver Block",
    #     rarity_per_mille=30,
    #     image_url="https://example.com/someimg.jpg",
    #     stats=AggregatedStats(count=1, floor=1.75),
    # )

    return mock
