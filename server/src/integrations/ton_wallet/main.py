from src.wallet.ton import create_wallet

from .manager import WalletManager


def create_wallet_manager():
    return WalletManager(wallet=create_wallet())


wallet_manager = create_wallet_manager()
