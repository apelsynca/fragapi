from abc import ABC, abstractmethod

import structlog
from aiogram.exceptions import TelegramNotFound

from src.bot import create_bot
from src.config import settings
from src.enums import TelegramLogSender as TelegramLogSenderType
from src.logging import Logger

log: Logger = structlog.get_logger()


class TelegramLogChatNotFound(Exception):
    pass


class BaseTelegramLogSender(ABC):
    @abstractmethod
    async def send(self, chat_id: int, text: str, with_notification: bool) -> None:
        pass


class LoggingTelegramLogSender(BaseTelegramLogSender):
    async def send(self, chat_id: int, text: str, with_notification: bool) -> None:
        log.info(
            "Sending user telegram log",
            chat_id=chat_id,
            text=text,
            with_notification=with_notification,
        )


class TelegramLogSender(BaseTelegramLogSender):
    def __init__(self) -> None:
        self.bot = create_bot()

    async def send(self, chat_id: int, text: str, with_notification: bool) -> None:
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_notification=not with_notification,
            )
        except TelegramNotFound:
            raise TelegramLogChatNotFound()


telegram_log_sender: BaseTelegramLogSender
if settings.TELEGRAM_LOG_SENDER == TelegramLogSenderType.chat:
    telegram_log_sender = TelegramLogSender()
else:
    telegram_log_sender = LoggingTelegramLogSender()
