import structlog
from aiogram import Bot

from src.config import settings
from src.logging import Logger

log: Logger = structlog.get_logger()


async def setup_webhook(bot: Bot) -> None:
    webhook_url = settings.BASE_URL + settings.BOT_WEBHOOK_PATH
    webhook_info = await bot.get_webhook_info()
    log.info("Setting webhook, prev webhook info", webhook_info=webhook_info)

    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query"],
        secret_token=settings.BOT_WEBHOOK_SECRET_TOKEN,
    )
