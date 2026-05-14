from unittest.mock import MagicMock

import pytest
from tonutils.contracts import WalletV5R1

from src.wallet.manager import WalletManager


@pytest.fixture
def wallet() -> MagicMock:
    return MagicMock(spec=WalletV5R1)


@pytest.fixture
def wallet_manager(wallet: MagicMock) -> WalletManager:
    return WalletManager(ton_wallets=[wallet])
