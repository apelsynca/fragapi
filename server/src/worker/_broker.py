from taskiq import AsyncBroker, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

from src.config import settings
from src.worker._sqlalchemy import SQLAlchemyMiddleware


def get_scheduler(broker: AsyncBroker):
    return TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])


def get_broker() -> AsyncBroker:
    broker = AioPikaBroker(url=settings.amqp_url)

    broker.add_middlewares(SQLAlchemyMiddleware())

    return broker
