from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from ton_core import to_nano
from tonutils.contracts import WalletV5R1

from src.wallet.manager import WalletManager, WalletManagerError

# this is for single wallet implementation


@pytest.fixture
def wallet() -> MagicMock:
    return MagicMock(spec=WalletV5R1)


@pytest.fixture
def wallet_manager(wallet: MagicMock) -> WalletManager:
    return WalletManager(ton_wallets=[wallet])


@pytest.mark.asyncio
async def test_gets_balance(
    wallet_manager: WalletManager, mocker: MockerFixture
) -> None:
    wallet_mock = mocker.patch.object(wallet_manager, "wallet", spec=WalletV5R1)
    wallet_mock.balance = to_nano(7.262)

    balance = await wallet_manager.get_balance()
    assert balance == to_nano(7.262)


@pytest.mark.asyncio
async def test_gets_wallet_for_requested_amount(
    wallet_manager: WalletManager, mocker: MockerFixture
) -> None:
    wallet_mock = mocker.patch.object(wallet_manager, "wallet", spec=WalletV5R1)
    wallet_mock.balance = to_nano(1.6)

    wallet = await wallet_manager.get_wallet_for_amount(amount=1.25)
    assert wallet is not None


# later test gets the wallet with largest balance for amount


@pytest.mark.asyncio
async def test_raises_if_no_wallet_for_requested_amount(
    wallet_manager: WalletManager, mocker: MockerFixture
) -> None:
    wallet_mock = mocker.patch.object(wallet_manager, "wallet", spec=WalletV5R1)
    wallet_mock.balance = to_nano(6.24)  # lower

    with pytest.raises(WalletManagerError):
        await wallet_manager.get_wallet_for_amount(amount=6.25)


# @pytest.mark.asyncio
# async def test_abc():
#     pass
