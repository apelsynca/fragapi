from ._broker import get_broker, get_scheduler
from ._enqueue import TaskQueueManager, enqueue_task
from ._sqlalchemy import AsyncSessionMaker

broker = get_broker()
scheduler = get_scheduler(broker)

__all__ = (
    "AsyncSessionMaker",
    "TaskQueueManager",
    "broker",
    "enqueue_task",
    "scheduler",
)


# def actor(actor_name: str | None = None, **options):
#     def decorator(fn):
#         broker.task(fn, **options)
#         return fn
#
#     return decorator
#
#
# @actor(actor_name="someone")
# def abc():
#     pass
