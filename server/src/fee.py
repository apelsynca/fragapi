from decimal import Decimal

from src.config import settings

TON_FEE = Decimal("0.00582")  # 0.00582 TON in general


def after_fee(amount: Decimal) -> Decimal:
    return amount + (amount * Decimal(str(settings.API_PRICE_MARKUP)))


def after_ton_network_fee(amount: Decimal) -> Decimal:
    """Calculate amount with TON blockchain fee's"""
    return amount + TON_FEE
