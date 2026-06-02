from unittest.mock import MagicMock

import pytest
from tonutils.contracts import WalletV5R1

from src.integrations.ton_wallet.manager import WalletManager
from src.postgres import AsyncSession
from src.worker import TaskQueueManager, broker
from src.worker._enqueue import _task_queue_manager


@pytest.fixture(autouse=True)
def set_job_queue_manager_context() -> None:
    _task_queue_manager.set(TaskQueueManager())


class FakeWalletManager(WalletManager):
    def __init__(self) -> None:
        self.balance = 0

        wmock = MagicMock(spec=WalletV5R1)
        self.wallet = wmock

        self.amounts_log = []

    async def get_balance(self) -> int:
        return self.balance

    async def get_wallet_for_amount(self, amount: int) -> WalletV5R1:
        self.amounts_log.append(amount)
        return self.wallet


@pytest.fixture
def wallet_manager() -> WalletManager:
    return FakeWalletManager()


@pytest.fixture(autouse=True)
def patch_worker_dependencies(wallet_manager: MagicMock, session: AsyncSession):
    broker.add_dependency_context(
        {AsyncSession: session, WalletManager: wallet_manager}
    )

    yield

    broker.custom_dependency_context = {}
