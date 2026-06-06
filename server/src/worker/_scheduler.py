from taskiq import AsyncBroker, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource


def get_scheduler(broker: AsyncBroker) -> TaskiqScheduler:
    return TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
