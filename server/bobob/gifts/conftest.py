import pytest

from src.gifts.service import gift as gift_service


@pytest.fixture(autouse=True)
def gift_models_json() -> dict:
    data = {"plushpepe": ["ssanina"]}

    gift_service.data = data

    return data
