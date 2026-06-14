from unittest.mock import MagicMock

import pytest
from tonutils.contracts import WalletV5R1

from src.postgres import AsyncSession, get_db_session
from src.wallet.manager import WalletManager
from src.worker import TaskQueueManager, broker
from src.worker._enqueue import _task_queue_manager
from src.worker.wallet_manager import get_wallet_manager


@pytest.fixture(autouse=True)
def set_job_queue_manager_context() -> None:
    _task_queue_manager.set(TaskQueueManager())


class FakeWalletManager(WalletManager):
    def __init__(self) -> None:
        self.balance = 0

        wmock = MagicMock(spec=WalletV5R1)
        self.wallet = wmock

    async def get_balance(self) -> int:
        return self.balance

    async def get_wallet_for_amount(self, amount: int) -> WalletV5R1:
        return self.wallet


@pytest.fixture
def wallet_manager() -> WalletManager:
    return FakeWalletManager()


@pytest.fixture(autouse=True)
def patch_worker_dependencies(wallet_manager: MagicMock, session: AsyncSession):
    broker.dependency_overrides[get_db_session] = lambda: session
    broker.dependency_overrides[get_wallet_manager] = lambda: wallet_manager

    yield

    broker.dependency_overrides.pop(get_db_session)
