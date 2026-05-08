from fastapi import Request

from src.wallet.manager import WalletManager


def get_wallet_manager(request: Request) -> WalletManager:
    return request.state.wallet_manager
