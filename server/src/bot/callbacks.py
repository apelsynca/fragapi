from telegram.ext import Application

from src.bot.menu.callbacks import setup_callbacks as setup_menu_callbacks


def setup_callbacks(application: Application) -> None:
    setup_menu_callbacks(application)
