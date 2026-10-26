import pytest

from src.config import settings
from src.fee import TON_FEE, fee_calculator


@pytest.mark.parametrize("amount", [1, 0.2582, 3.251, 999, 2581.25])
def test_with_markup(amount: float) -> None:
    result = fee_calculator.with_markup(amount)
    assert result == amount * (1 + settings.API_PRICE_MARKUP)


@pytest.mark.parametrize("amount", [1, 0.2582, 3.251, 999, 2581.25])
def test_with_network_fee(amount: float) -> None:
    assert fee_calculator.with_network_fee(amount) == amount + TON_FEE


@pytest.mark.parametrize("amount", [1, 0.2582, 3.251, 999, 2581.25])
def test_total_cost_applies_network_fee_before_markup(amount: float) -> None:
    result = fee_calculator.total_cost(amount)
    assert result == (amount + TON_FEE) * (1 + settings.API_PRICE_MARKUP)


@pytest.mark.parametrize("amount", [1, 0.2582, 3.251, 999, 2581.25])
def test_approx_before_fees_reverts_total_cost(amount: float) -> None:
    total = fee_calculator.total_cost(amount)
    assert fee_calculator.approx_before_fees(total) == pytest.approx(amount)


@pytest.mark.parametrize("total", [0, TON_FEE])
def test_approx_before_fees_zero_within_network_fee(total: float) -> None:
    assert fee_calculator.approx_before_fees(total) == 0
