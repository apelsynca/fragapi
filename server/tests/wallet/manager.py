from unittest.mock import MagicMock

import pytest
from tonutils.contracts import WalletV5R1

from src.wallet.manager import WalletManager


@pytest.fixture
def wallet_mock() -> MagicMock:
    return MagicMock(spec=WalletV5R1)


async def test_get_balance_refreshes_and_returns_right(wallet_mock: MagicMock) -> None:
    wallet_mock.balance = 52
    wallet_manager = WalletManager(wallet=wallet_mock)

    balance = await wallet_manager.get_balance()

    wallet_mock.refresh.assert_called_once()
    assert balance == 52
