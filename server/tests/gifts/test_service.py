import pytest

from src.exceptions import ResourceNotFound
from src.gifts.service import gift as gift_service


@pytest.mark.asyncio
async def test_gets_right_gift_models(gift_models_json: dict) -> None:
    assert "plushpepe" in gift_models_json

    models = await gift_service.get_models_by_shortname("plushpepe")

    assert models == gift_models_json["plushpepe"]


@pytest.mark.asyncio
async def test_raises_wrong_gift_shortname(gift_models_json: dict) -> None:
    assert "wrongitem" not in gift_models_json

    with pytest.raises(ResourceNotFound):
        await gift_service.get_models_by_shortname("wrongitem")
