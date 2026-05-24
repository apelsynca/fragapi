import structlog
from ton_core import NetworkGlobalID
from tonutils.contracts import WalletV5R1

from src.config import settings
from src.logging import Logger
from src.wallet.ton import toncenter as toncenter_client

if settings.is_production():
    env_network_id = NetworkGlobalID.MAINNET
else:
    env_network_id = NetworkGlobalID.TESTNET

log: Logger = structlog.get_logger()


class WalletManagerError(Exception):
    pass


class WalletManager:
    """
    Service of a global FragAPI wallet

    Since the wallets can be split
    """

    def __init__(self, wallet: WalletV5R1) -> None:
        self.wallet = wallet
        # self.wallet = create_wallet()

    async def get_balance(self) -> int:
        await self.wallet.refresh()
        return self.wallet.balance

    async def get_wallet_for_amount(self, amount: int) -> WalletV5R1:
        selected_wallet = self.wallet
        await selected_wallet.refresh()

        if selected_wallet.balance <= amount:
            raise WalletManagerError(
                f"There is no wallet with balance for required amount = {amount}"
            )

        return selected_wallet

    async def __aenter__(self):
        await toncenter_client.__aenter__()

    async def __aexit__(self, *args, **kwargs):
        await toncenter_client.__aexit__(*args, **kwargs)
