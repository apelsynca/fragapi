from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from tonutils.contracts import WalletV5R1

from src.integrations.ton_wallet.manager import WalletManager
from src.worker import TaskQueueManager
from src.worker._enqueue import _task_queue_manager
from src.worker._sqlalchemy import SQLAlchemyMiddleware
from src.worker._wallet_manager import WalletManagerMiddleware


@pytest.fixture(autouse=True)
def set_job_queue_manager_context() -> None:
    _task_queue_manager.set(TaskQueueManager())


class FakeWalletManager(WalletManager):
    def __init__(self) -> None:
        self.balance = 0
        self.return_wallet = MagicMock(spec=WalletV5R1)

        self.amounts_log = []

    async def get_balance(self) -> int:
        return self.balance

    async def get_wallet_for_amount(self, amount: int) -> WalletV5R1:
        self.amounts_log.append(amount)
        return self.return_wallet


@pytest.fixture
def wallet_manager() -> WalletManager:
    return FakeWalletManager()


@pytest.fixture(autouse=True)
def patch_middlewares(
    mocker: MockerFixture, wallet_manager: MagicMock, session: AsyncSession
) -> None:
    mocker.patch.object(SQLAlchemyMiddleware, "get_async_session", return_value=session)
    mocker.patch.object(WalletManagerMiddleware, "get", return_value=wallet_manager)
