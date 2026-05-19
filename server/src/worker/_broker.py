import structlog
from taskiq import (
    AsyncBroker,
    InMemoryBroker,
    TaskiqMessage,
    TaskiqMiddleware,
    TaskiqResult,
    TaskiqScheduler,
)
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

from src.config import settings
from src.worker._sqlalchemy import SQLAlchemyMiddleware
from src.worker._wallet_manager import WalletManagerMiddleware


class StructlogMiddleware(TaskiqMiddleware):
    def pre_execute(
        self,
        message: TaskiqMessage,
    ):
        # taskiq_task_id=message.task_id,
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(taskiq_task_name=message.task_name)

        return message

    async def on_error(
        self, message: TaskiqMessage, result: "TaskiqResult", exception: BaseException
    ):
        log = structlog.get_logger()
        log.error(
            "Task failed",
            task_name=message.task_name,
            task_id=message.task_id,
            exc_info=exception,
        )
        # Re‑raise if you want the broker to still handle it (e.g., retry)
        # raise exception


def get_broker() -> AsyncBroker:
    if settings.is_testing():
        broker = InMemoryBroker(await_inplace=True)
    else:
        broker = AioPikaBroker(url=settings.amqp_url)

    broker.add_middlewares(
        StructlogMiddleware(), SQLAlchemyMiddleware(), WalletManagerMiddleware()
    )

    return broker


def get_scheduler(broker: AsyncBroker) -> TaskiqScheduler:
    return TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
