import functools
from collections.abc import Awaitable, Callable
from typing import Any

from taskiq import AsyncTaskiqDecoratedTask

from ._broker import get_broker
from ._enqueue import TaskQueueManager, enqueue_task
from ._scheduler import get_scheduler

broker = get_broker()
scheduler = get_scheduler(broker)


def worker_task_with_queue_manager[**P, R](
    task_name: str | None = None,
    **labels: Any,
):
    """
    WARN: this decorator is unclean, we need a middleware to provides `enqueue_task` that can 'enqueue_task'
          because even tho this works, it does not allow for testable env, which is usually bad.
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
)
