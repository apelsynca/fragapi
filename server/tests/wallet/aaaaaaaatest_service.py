from datetime import datetime, timedelta

import pytest

from src.wallet.manager import WalletManager
from src.wallet.service import wallet as wallet_service
from src.wallet.types import TonConnectTransaction


@pytest.mark.asyncio
async def test_tries_to_send_from_tc(wallet_manager: WalletManager) -> None:
    transaction = TonConnectTransaction(
        valid_until=datetime.now() + timedelta(minutes=3), from_address="", messages=[]
    )

    message_hash = await wallet_service.transfer_from_tc(
        wallet_manager=wallet_manager, transaction=transaction
    )

    assert message_hash is not None
