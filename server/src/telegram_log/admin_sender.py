from abc import ABC, abstractmethod

import structlog
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

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
    def __init__(self) -> None:
        self.bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    async def send(self, text: str, with_notification: bool) -> None:
        await self.bot.send_message(
            chat_id=settings.ADMIN_TELEGRAM_LOGS_CHAT_ID,
            text=text,
            disable_notification=not with_notification,
        )


admin_telegram_log_sender: BaseAdminTelegramLogSender
if settings.TELEGRAM_LOG_SENDER == TelegramLogSenderType.chat:
    admin_telegram_log_sender = AdminTelegramLogSender()
else:
    admin_telegram_log_sender = LoggingAdminTelegramLogSender()
