from ton_core import NetworkGlobalID
from tonutils.contracts import WalletV5R1

from src.config import settings
from src.wallet.ton import get_wallet

if settings.is_production():
    env_network_id = NetworkGlobalID.MAINNET
else:
    env_network_id = NetworkGlobalID.TESTNET


class WalletManager:
    """
    Service of a global FragAPI wallet

    Since the wallets can be split
    """

    def __init__(self) -> None:
        self.ton_wallet: WalletV5R1 = get_wallet()
