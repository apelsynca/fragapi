from ton_core import NetworkGlobalID
from tonutils.contracts import WalletV5R1

from src.config import settings
from src.kit.ton_connect import TonConnect
from src.wallet.ton import create_wallet

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
        self.ton_wallet: WalletV5R1 = create_wallet()

    def get_ton_connect(self, tc_domain: str) -> TonConnect:
        return TonConnect(self.ton_wallet, tc_domain=tc_domain)

    async def get_balance(self) -> float:
        return 0
