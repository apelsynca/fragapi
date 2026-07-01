import pytest

from src.config import settings
from src.fee import after_fee


@pytest.mark.parametrize("amount", [1, 0.2582, 3.251, 999, 2581.25])
def test_after_fee(amount: int) -> None:
    result = after_fee(amount)
    assert result == amount * (1 + settings.API_PRICE_MARKUP)
