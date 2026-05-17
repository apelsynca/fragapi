from taskiq import TaskiqMiddleware

from src.integrations.ton_wallet.manager import WalletManager
from src.logging import get_logger
from src.wallet.ton import create_wallet

log = get_logger()

_wallet_manager: WalletManager | None = None


def create_wm() -> WalletManager:
    wallet = create_wallet()  # for now
    return WalletManager(wallet=wallet)


class WalletManagerMiddleware(TaskiqMiddleware):
    @classmethod
    def get(cls) -> WalletManager:
        global _wallet_manager
        if _wallet_manager is None:
            raise RuntimeError("Redis not initialized")
        return _wallet_manager

    async def startup(self) -> None:
        global _wallet_manager
        _wallet_manager = create_wm()
        log.info("Created WalletManager")
