import random
from typing import Any

import structlog
from aiogram.exceptions import TelegramRetryAfter
from taskiq import AsyncTaskiqDecoratedTask

from src.logging import Logger
from src.worker import broker

from .admin_sender import admin_telegram_log_sender, admin_telegram_notification_sender
from .sender import TelegramLogChatNotFound, telegram_log_sender

log: Logger = structlog.get_logger()

MAX_FLOOD_RETRIES = 5


async def _retry_after_flood(
    task: AsyncTaskiqDecoratedTask,
    exc: TelegramRetryAfter,
    attempt: int,
    **kwargs: Any,
) -> None:
    """Telegram said 429: send the same message again once it allows us to."""
    if attempt >= MAX_FLOOD_RETRIES:
        log.error("telegram_log.flood_retries_exhausted", task_name=task.task_name)
        raise exc

    # Jitter keeps a rate limited burst from coming back all at once.
    delay = int(exc.retry_after) + random.randint(1, 5)
    log.warning(
        "telegram_log.flood_retry_scheduled",
        task_name=task.task_name,
        delay=delay,
        attempt=attempt + 1,
    )
    await task.kicker().with_labels(delay=delay).kiq(**kwargs, attempt=attempt + 1)


@broker.task(task_name="telegram_log.send")
async def telegram_log_send(
    chat_id: int, text: str, with_notification: bool = False, attempt: int = 0
) -> None:
    try:
        await telegram_log_sender.send(
            chat_id=chat_id, text=text, with_notification=with_notification
        )
    except TelegramLogChatNotFound:
        log.info("telegram_log.send.chat_not_found", chat_id=chat_id)
    except TelegramRetryAfter as exc:
        await _retry_after_flood(
            telegram_log_send,
            exc,
            attempt,
            chat_id=chat_id,
            text=text,
            with_notification=with_notification,
        )
    except Exception:
        log.exception("telegram_log.send.error")
        raise


@broker.task(task_name="admin_telegram_notification.send")
async def admin_telegram_notification_send(
    text: str, with_notification: bool, attempt: int = 0
) -> None:
    try:
        await admin_telegram_notification_sender.send(
            text=text, with_notification=with_notification
        )
    except TelegramRetryAfter as exc:
        await _retry_after_flood(
            admin_telegram_notification_send,
            exc,
            attempt,
            text=text,
            with_notification=with_notification,
        )
    except Exception:
        log.exception("admin_telegram_notification.send.error")
        raise


@broker.task(task_name="admin_telegram_log.send")
async def admin_telegram_log_send(
    text: str, with_notification: bool, attempt: int = 0
) -> None:
    try:
        await admin_telegram_log_sender.send(
            text=text, with_notification=with_notification
        )
    except TelegramRetryAfter as exc:
        await _retry_after_flood(
            admin_telegram_log_send,
            exc,
            attempt,
            text=text,
            with_notification=with_notification,
        )
    except Exception:
        log.exception("admin_telegram_log.send.error")
        raise
