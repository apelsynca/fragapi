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


class StructlogMiddleware(TaskiqMiddleware):
    def pre_execute(
        self,
        message: TaskiqMessage,
    ):
        # trace_id = TraceID.set()
        # source_trace_id = message.labels.get("source_trace_id")
        # print("Labels", message.labels, trace_id, source_trace_id)

        print("pre execute pre")
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(taskiq_task_name=message.task_name)
        print("pre execute post")

        log = structlog.get_logger()
        log.warning("WARNING LOG")

        return message

    async def on_error(
        self, message: TaskiqMessage, result: "TaskiqResult", exception: BaseException
    ):
        print("On error")
        log = structlog.get_logger()
        log.error(
            "Task failed",
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
