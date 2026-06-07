import structlog

from src.logging import Logger

log: Logger = structlog.get_logger()


class LoggerTelegramLogSender:
    async def send(self, text: str, with_notification: bool) -> None:
        log.info("Sending telegram log", text=text, with_notification=with_notification)


telegram_log_sender = LoggerTelegramLogSender()
