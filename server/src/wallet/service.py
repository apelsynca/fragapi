from ton_core import NetworkGlobalID

from src.config import settings

if settings.is_production():
    env_network_id = NetworkGlobalID.MAINNET
else:
    env_network_id = NetworkGlobalID.TESTNET


class WalletService:
    async def transfer_from_tc() -> None:
        raise


wallet = WalletService()
