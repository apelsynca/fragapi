from unittest.mock import MagicMock

import pytest

from src.wallet.manager import WalletManager


@pytest.fixture(autouse=True)
def wallet_manager() -> WalletManager:
    return MagicMock(spec=WalletManager)
