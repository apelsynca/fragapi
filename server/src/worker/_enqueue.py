import contextlib
import contextvars
from typing import Any

import structlog
from taskiq import AsyncTaskiqDecoratedTask

from src.logging import Logger

log: Logger = structlog.get_logger()

_task_queue_manager: contextvars.ContextVar["TaskQueueManager | None"] = (
    contextvars.ContextVar("app.task_queue_manager")
)


class TaskQueueManager:
    def __init__(self) -> None:
        self._enqueued_tasks: list[
            tuple[AsyncTaskiqDecoratedTask, tuple, dict[str, Any]]
        ] = []

    @classmethod
    @contextlib.asynccontextmanager
    async def open(cls):
        task_queue_manager = cls()
        _task_queue_manager.set(task_queue_manager)
        try:
            yield task_queue_manager
            await task_queue_manager.process_queue()
        finally:
            task_queue_manager.reset()
            _task_queue_manager.set(None)

    async def process_queue(self) -> None:
        for taskiq_job, args, kwargs in self._enqueued_tasks:
            await taskiq_job.kiq(*args, **kwargs)
        self.reset()

    def reset(self) -> None:
        self._enqueued_tasks = []

    def enqueue(self, taskiq_task: AsyncTaskiqDecoratedTask, *args, **kwargs) -> None:
        self._enqueued_tasks.append((taskiq_task, args, kwargs))
        log.debug("app.worker.task_enqueued", job=taskiq_task.task_name)

    @classmethod
    def get(cls) -> "TaskQueueManager":
        task_queue_manager = _task_queue_manager.get()
        if task_queue_manager is None:
            raise RuntimeError("JobQueueManager not initialized")
        return task_queue_manager


def enqueue_task(taskiq_task: AsyncTaskiqDecoratedTask, *args, **kwargs) -> None:
    job_queue_manager = TaskQueueManager.get()
    job_queue_manager.enqueue(taskiq_task, *args, **kwargs)
