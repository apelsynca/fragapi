from unittest.mock import MagicMock

import pytest
from tonutils.contracts import WalletV5R1

from src.wallet.manager import WalletManager


@pytest.fixture
def ton_wallet() -> MagicMock:
    return MagicMock(spec=WalletV5R1)


@pytest.mark.asyncio
async def test_get_balance(ton_wallet: MagicMock) -> None:
    ton_wallet.balance = 10

    wmanager = WalletManager(ton_wallet=ton_wallet)

    balance = await wmanager.get_balance()

    assert balance == 10
