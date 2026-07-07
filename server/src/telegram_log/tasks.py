import structlog

from src.logging import Logger
from src.worker import broker

from .sender import TelegramLogChatNotFound, telegram_log_sender

log: Logger = structlog.get_logger()


@broker.task(task_name="telegram_log.send")
async def telegram_log_send(
    chat_id: int, text: str, with_notification: bool = False
) -> None:
    try:
        await telegram_log_sender.send(
            chat_id=chat_id, text=text, with_notification=with_notification
        )
    except TelegramLogChatNotFound:
        log.info("telegram_log.send.chat_not_found", chat_id=chat_id)
    except Exception as e:
        log.error("telegram_log.send.error", exc_info=True)
        raise e
