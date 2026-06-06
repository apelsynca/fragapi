import structlog

from src.logging import Logger
from src.worker import broker

log: Logger = structlog.get_logger()


@broker.task(schedule=[{"interval": 3, "args": ["Myprint string"]}])
async def task_interval_half_and_one_second(print_string: str) -> None:
    print(print_string, "<- print string")
    log.warning("Get logger")


@broker.task(schedule=[{"cron": "* * * * *"}])  # every minute
async def dummy_periodic():
    print("Scheduled task ran")
    log.warning("Get logger")
