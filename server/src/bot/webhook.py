import structlog
from aiogram import Bot

from src.config import settings
from src.logging import Logger

log: Logger = structlog.get_logger()


async def setup_webhook(bot: Bot) -> None:
    if settings.BASE_URL.startswith("http://"):
        log.warning(
            "Skipping setting up webhook, since base url is http.",
            base_url=settings.BASE_URL,
        )
        return

    webhook_url = settings.BASE_URL + settings.BOT_WEBHOOK_PATH
    webhook_info = await bot.get_webhook_info()

    url_matches = False
    allowed_updates_match = False

    if webhook_info.url == webhook_url:
        log.debug("Bot webhook, already right url", info_url=webhook_info.url)
        url_matches = True

    allowed_updates = ["message", "callback_query", "inline_query"]

    if webhook_info.allowed_updates is not None and set(
        webhook_info.allowed_updates
    ) == set(allowed_updates):
        log.debug(
            "Bot webhook, already right allowed_updates",
            info_updates=webhook_info.allowed_updates,
        )
        allowed_updates_match = True

    if url_matches and allowed_updates_match:
        log.debug("Bot webhook setting skip, url and updates are right")
        return

    log.debug(
        "Setting up telegram bot webhook",
        new_url=webhook_url,
        prev_url=webhook_info.url,
    )

    result = await bot.set_webhook(
        url=webhook_url,
        allowed_updates=allowed_updates,
        secret_token=settings.BOT_WEBHOOK_SECRET_TOKEN,
    )
    log.info("Telegram bot webhook set", url=webhook_url, result=result)
