from telegram.constants import ParseMode
from telegram.ext import Application, Defaults

from src.config import settings


def get_bot_application() -> Application:
    defaults = Defaults(parse_mode=ParseMode.HTML)
    return (
        Application.builder()
        .token(settings.bot.token.get_secret_value())
        .updater(None)
        .defaults(defaults)
        .build()
    )


bot_application = get_bot_application()
