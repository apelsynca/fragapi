import functools
from collections.abc import Awaitable, Callable
from typing import Any

from taskiq import AsyncTaskiqDecoratedTask

from ._broker import get_broker, get_scheduler
from ._enqueue import TaskQueueManager, enqueue_task

broker = get_broker()
scheduler = get_scheduler(broker)


def worker_task[**P, R](
    task_name: str | None = None,
    **labels: Any,
):
    """
    WARN: this is bad, we need a middleware to provide good `enqueue_task`
          because this even tho works, does not allow for testable env
          which is bad.
    """

    def decorator(
        fn: Callable[P, Awaitable[R]],
    ) -> AsyncTaskiqDecoratedTask[P, Awaitable[R]]:
        @functools.wraps(fn)
        async def _wrapped_fn(*args: P.args, **kwargs: P.kwargs) -> R:
            async with TaskQueueManager.open():
                return await fn(*args, **kwargs)

        return broker.register_task(func=_wrapped_fn, task_name=task_name, **labels)

    return decorator


__all__ = (
    "TaskQueueManager",
    "broker",
    "enqueue_task",
    "scheduler",
)
