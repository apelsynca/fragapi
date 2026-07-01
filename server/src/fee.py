from src.config import settings

TON_FEE = 0.00582  # 0.00582 TON in general


def after_fee(amount: float) -> float:
    return amount * (1 + settings.API_PRICE_MARKUP)


def approx_before_fee(amount: float) -> float:
    if amount <= TON_FEE:
        return 0
    return amount / (1 + settings.API_PRICE_MARKUP) - TON_FEE


def after_ton_network_fee(amount: float) -> float:
    """Calculate amount with TON blockchain fee's"""
    return amount + TON_FEE
