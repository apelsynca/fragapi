from src.config import settings

TON_FEE = 0.00582  # 0.00582 GRAM in general


class FeeCalculator:
    """
    Single source of truth for purchase pricing.

    total cost = (amount + TON network fee) * (1 + API markup)
    """

    @property
    def ton_network_fee(self) -> float:
        return TON_FEE

    @property
    def markup(self) -> float:
        # Read on every call so settings changes (and test patches) apply.
        return settings.API_PRICE_MARKUP

    def with_network_fee(self, amount: float) -> float:
        """Amount plus the TON blockchain fee."""
        return amount + self.ton_network_fee

    def with_markup(self, amount: float) -> float:
        """Amount plus the API markup."""
        return amount * (1 + self.markup)

    def total_cost(self, amount: float) -> float:
        """What the user is charged for sending `amount` GRAM."""
        return self.with_markup(self.with_network_fee(amount))

    def approx_before_fees(self, total: float) -> float:
        """Approximate inverse of `total_cost` (0 for totals within the TON fee)."""
        if total <= self.ton_network_fee:
            return 0
        return total / (1 + self.markup) - self.ton_network_fee


fee_calculator = FeeCalculator()
