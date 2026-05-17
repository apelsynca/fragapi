from taskiq import AsyncBroker, InMemoryBroker, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

from src.config import settings
from src.worker._sqlalchemy import SQLAlchemyMiddleware
from src.worker._wallet_manager import WalletManagerMiddleware


def get_scheduler(broker: AsyncBroker):
    return TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])


def get_broker() -> AsyncBroker:
    if settings.is_testing():
        broker = InMemoryBroker(await_inplace=True)
    else:
        broker = AioPikaBroker(url=settings.amqp_url)

    broker.add_middlewares(SQLAlchemyMiddleware(), WalletManagerMiddleware())

    return broker
