from telegram.ext import Application

from src.bot.callbacks import setup_callbacks
from src.bot.webhook import setup_bot_webhook


async def setup_bot(application: Application):
    setup_callbacks(application)
    await setup_bot_webhook(bot=application.bot)
