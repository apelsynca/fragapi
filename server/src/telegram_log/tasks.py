from src.worker import broker

from .sender import telegram_log_sender


@broker.task
async def telegram_log_send(
    chat_id: int, text: str, with_notification: bool = False
) -> None:
    await telegram_log_sender.send(
        chat_id=chat_id, text=text, with_notification=with_notification
    )
