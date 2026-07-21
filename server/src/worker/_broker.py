import structlog
from taskiq import (
    AsyncBroker,
    InMemoryBroker,
    TaskiqMessage,
    TaskiqMiddleware,
    TaskiqResult,
)
from taskiq_aio_pika import AioPikaBroker

from src.config import settings
from src.logging import Logger, TraceID

log: Logger = structlog.get_logger()


class StructlogMiddleware(TaskiqMiddleware):
    def pre_execute(
        self,
        message: TaskiqMessage,
    ):
        trace_id = TraceID.set()
        source_trace_id = message.labels.get("source_trace_id")

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            task_name=message.task_name,
            task_id=message.task_id,
            trace_id=trace_id,
            source_trace_id=source_trace_id,
        )

        return message

    async def on_error(
        self, message: TaskiqMessage, result: "TaskiqResult", exception: BaseException
    ):
        log.error(
            "app.worker.task_failed",
            task_name=message.task_name,
            task_id=message.task_id,
            exc_info=exception,
        )

        super().on_error(message, result, exception)


def get_broker() -> AsyncBroker:
    if settings.is_testing():
        broker = InMemoryBroker()
    else:
        broker = AioPikaBroker(url=settings.amqp_url)

    broker.add_middlewares(StructlogMiddleware())

    return broker
