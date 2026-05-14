from unittest.mock import MagicMock

import pytest
from ton_core import to_nano
from tonutils.contracts import WalletV5R1

from src.wallet.manager import WalletManager


@pytest.fixture
def wallet() -> MagicMock:
    wallet = MagicMock(spec=WalletV5R1)
    wallet.balance = to_nano(0)

    return wallet


@pytest.fixture
def wallet_manager(wallet: MagicMock) -> WalletManager:
    return WalletManager(ton_wallets=[wallet])
