from src.config import settings

TON_FEE = 0.00582  # 0.00582 TON in general


def after_fee(amount: float) -> float:
    return amount + (amount * settings.API_PRICE_MARKUP)


def after_ton_network_fee(amount: float) -> float:
    """Calculate amount with TON blockchain fee's"""
    return amount + TON_FEE
