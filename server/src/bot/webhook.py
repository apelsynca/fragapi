import os
from collections.abc import Sequence
from typing import cast

from telegram import Bot, Update, WebhookInfo
from telegram.error import NetworkError

from src.config import settings
from src.logging import get_logger

log = get_logger()


async def setup_bot_webhook(bot: Bot) -> None:
    try:
        webhook_info = cast(WebhookInfo, await bot.get_webhook_info())
    except NetworkError as exc:
        log.error("Error while getting webhook info", error=exc)
        log.debug("Webhook was not set.")
        return

    webhook_url = settings.BOT_WEBHOOK_URL + settings.BOT_WEBHOOK_PATH
    log.info("ABC", webhook_info=webhook_info, webhook_url=webhook_url)
    allowed_updates = (Update.MESSAGE, Update.CALLBACK_QUERY)

    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=allowed_updates,
        secret_token=settings.BOT_WEBHOOK_SECRET_TOKEN,
    )


def need_to_update_webhook(
    webhook_info: WebhookInfo, url: str, allowed_updates: Sequence[str]
) -> bool:
    force_webhook = bool(int(os.getenv("FORCE_WEBHOOK", "0")))
    if force_webhook:
        log.info("Forcing webhook update from env value", force_webhook=force_webhook)
        return True

    need_update_webhook_url = webhook_info.url != url
    if need_update_webhook_url:
        log.info(
            "Changing webhook url",
            current=url,
            previous=webhook_info.url,
        )

    need_update_webhook_allowed_updates = set(webhook_info.allowed_updates) != set(
        allowed_updates
    )
    if need_update_webhook_allowed_updates:
        log.info(
            "Changing webhook allowed updates",
            prev=webhook_info.allowed_updates,
            curr=allowed_updates,
        )

    return need_update_webhook_url or need_update_webhook_allowed_updates
