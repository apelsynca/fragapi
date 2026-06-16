from abc import ABC, abstractmethod

import structlog
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings
from src.enums import TelegramLogSender as TelegramLogSenderType
from src.logging import Logger

log: Logger = structlog.get_logger()


class BaseTelegramLogSender(ABC):
    @abstractmethod
    async def send(self, text: str, with_notification: bool) -> None:
        pass


class LoggingTelegramLogSender(BaseTelegramLogSender):
    async def send(self, text: str, with_notification: bool) -> None:
        log.info(
            "Sending admin telegram log", text=text, with_notification=with_notification
        )


class TelegramLogSender(BaseTelegramLogSender):
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


telegram_log_sender: BaseTelegramLogSender
if settings.TELEGRAM_LOG_SENDER == TelegramLogSenderType.chat:
    telegram_log_sender = TelegramLogSender()
else:
    telegram_log_sender = LoggingTelegramLogSender()
