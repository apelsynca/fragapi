from src import tasks
from src.logging import configure as configure_logging
from src.worker import broker

from ._broker import get_scheduler

configure_logging(logtide_service="worker")

scheduler = get_scheduler(broker)

__all__ = ["broker", "scheduler", "tasks"]
