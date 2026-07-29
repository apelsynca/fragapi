from abc import ABC, abstractmethod

import structlog

from src.bot import create_bot
from src.config import settings
from src.enums import TelegramLogSender as TelegramLogSenderType
from src.logging import Logger

log: Logger = structlog.get_logger()


class BaseAdminTelegramLogSender(ABC):
    @abstractmethod
    async def send(self, text: str, with_notification: bool) -> None:
        pass


class LoggingAdminTelegramLogSender(BaseAdminTelegramLogSender):
    async def send(self, text: str, with_notification: bool) -> None:
        log.info(
            "Sending admin telegram log", text=text, with_notification=with_notification
        )


class AdminTelegramLogSender(BaseAdminTelegramLogSender):
    def __init__(self, chat_id: int | str) -> None:
        self.bot = create_bot()
        self.chat_id = chat_id

    async def send(self, text: str, with_notification: bool) -> None:
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            disable_notification=not with_notification,
        )


admin_telegram_notification_sender: BaseAdminTelegramLogSender
if settings.TELEGRAM_LOG_SENDER == TelegramLogSenderType.chat:
    admin_telegram_notification_sender = AdminTelegramLogSender(
        chat_id=settings.ADMIN_TELEGRAM_NOTIFICATIONS_CHAT_ID
    )
else:
    admin_telegram_notification_sender = LoggingAdminTelegramLogSender()

admin_telegram_log_sender: BaseAdminTelegramLogSender
if settings.TELEGRAM_LOG_SENDER == TelegramLogSenderType.chat:
    admin_telegram_log_sender = AdminTelegramLogSender(
        chat_id=settings.ADMIN_TELEGRAM_LOGS_CHAT_ID
    )
else:
    admin_telegram_log_sender = LoggingAdminTelegramLogSender()
