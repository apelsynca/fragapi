import structlog
from aiogram import Bot

from src.config import settings
from src.logging import Logger

log: Logger = structlog.get_logger()


async def setup_webhook(bot: Bot) -> None:
    webhook_url = settings.BASE_URL + settings.BOT_WEBHOOK_PATH
    webhook_info = await bot.get_webhook_info()

    if webhook_info.url == webhook_url:
        log.debug(
            "Skipped setting bot webhook, already right url", info_url=webhook_info.url
        )
        return

    allowed_updates = ["message", "callback_query"]
    if webhook_info.allowed_updates is not None and set(
        webhook_info.allowed_updates
    ) == set(allowed_updates):
        return

    log.info(
        "Setting up telegram bot webhook",
        new_url=webhook_url,
        prev_url=webhook_info.url,
    )

    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=allowed_updates,
        secret_token=settings.BOT_WEBHOOK_SECRET_TOKEN,
    )
