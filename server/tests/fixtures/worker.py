from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.integrations.ton_wallet.manager import WalletManager
from src.worker import TaskQueueManager
from src.worker._enqueue import _task_queue_manager
from src.worker._sqlalchemy import SQLAlchemyMiddleware
from src.worker._wallet_manager import WalletManagerMiddleware


@pytest.fixture(autouse=True)
def set_job_queue_manager_context() -> None:
    _task_queue_manager.set(TaskQueueManager())


class MockWalletManager(WalletManager):
    def __init__(self) -> None:
        pass


@pytest.fixture
def wallet_manager() -> WalletManager:
    return MockWalletManager()


@pytest.fixture(autouse=True)
def patch_middlewares(
    mocker: MockerFixture, wallet_manager: MagicMock, session: AsyncSession
) -> None:
    mocker.patch.object(SQLAlchemyMiddleware, "get_async_session", return_value=session)
    mocker.patch.object(WalletManagerMiddleware, "get", return_value=wallet_manager)
