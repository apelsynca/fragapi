from abc import ABC, abstractmethod

import structlog
from telegram.constants import ParseMode
from telegram.ext import ExtBot

from src.config import settings
from src.enums import TelegramLogSender as TelegramLogSenderType
from src.logging import Logger

log: Logger = structlog.get_logger()


class TelegramLogSender(ABC):
    @abstractmethod
    async def send(self, text: str, with_notification: bool = False) -> None:
        raise NotImplementedError


class ChatTelegramLogSender(TelegramLogSender):
    def __init__(self) -> None:
        self.bot = ExtBot(token=settings.BOT_TOKEN)

    async def send(self, text: str, with_notification: bool = False) -> None:
        await self.bot.send_message(
            chat_id=settings.TELEGRAM_LOGS_CHAT_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_notification=not with_notification,
        )


class LoggingTelegramLogSender(TelegramLogSender):
    async def send(self, text: str, with_notification: bool = False) -> None:
        log.info("Telegram log", text=text, with_notification=with_notification)


# this is probably a bad place for that

telegram_log_sender: TelegramLogSender
if settings.TELEGRAM_LOG_SENDER == TelegramLogSenderType.chat:
    telegram_log_sender = ChatTelegramLogSender()
else:
    # Logging in development
    telegram_log_sender = LoggingTelegramLogSender()
