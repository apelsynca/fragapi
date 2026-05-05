from ton_core import NetworkGlobalID

from src.config import settings
from src.wallet.types import TonConnectTransaction

if settings.is_production():
    env_network_id = NetworkGlobalID.MAINNET
else:
    env_network_id = NetworkGlobalID.TESTNET


class WalletService:
    async def transfer_from_tc(self, transaction: TonConnectTransaction) -> str:
        return "somehash"

    async def get_balance(self) -> float:
        return 0


wallet = WalletService()
