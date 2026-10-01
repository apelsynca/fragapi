from collections.abc import AsyncGenerator

from src.config import settings
from src.wallet.send_gate import WalletSendGate, create_wallet_send_redis


async def get_wallet_send_gate() -> AsyncGenerator[WalletSendGate]:
    async with create_wallet_send_redis() as redis:
        yield WalletSendGate(redis, str(settings.TON_ADDRESS))
