import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.worker import TaskQueueManager
from src.worker._enqueue import _task_queue_manager
from src.worker._sqlalchemy import SQLAlchemyMiddleware


@pytest.fixture(autouse=True)
def set_job_queue_manager_context() -> None:
    _task_queue_manager.set(TaskQueueManager())


@pytest.fixture(autouse=True)
def patch_middlewares(mocker: MockerFixture, session: AsyncSession) -> None:
    mocker.patch.object(SQLAlchemyMiddleware, "get_async_session", return_value=session)
