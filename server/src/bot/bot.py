from telegram.constants import ParseMode
from telegram.ext import Application, Defaults

from src.bot.menu.callbacks import setup_callbacks as setup_menu_callbacks
from src.bot.utils.webhook import setup_bot_webhook
from src.config import settings


def get_bot_application() -> Application:
    defaults = Defaults(parse_mode=ParseMode.HTML)
    return (
        Application.builder()
        .token(settings.BOT_TOKEN)
        .updater(None)
        .defaults(defaults)
        .build()
    )


async def setup_bot(application: Application):
    setup_menu_callbacks(application)

    await setup_bot_webhook(bot=application.bot)
