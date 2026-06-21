import structlog

from src.logging import Logger
from src.worker import broker

from .sender import telegram_log_sender

# WARN: broker from 'src.worker' is probably temporary solution,
# best to move logic of admin logging to some different place (other than backoffice)

log: Logger = structlog.get_logger()


@broker.task(task_name="admin_telegram_log.send")
async def telegram_log_send(text: str, with_notification: bool) -> None:
    try:
        await telegram_log_sender.send(text=text, with_notification=with_notification)
    except Exception as e:
        log.error("admin_telegram_log.send.error", exc_info=True)
        raise e
