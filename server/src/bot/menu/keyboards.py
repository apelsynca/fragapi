from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.config import settings


def login(bot_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Войти",
                    url=f"{settings.PANEL_URL}/bot-login?hash={bot_hash}",
                )
            ]
        ]
    )


def panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌐 Панель",
                    url=settings.generate_panel_url("/"),
                    style="primary",
                )
            ],
            [InlineKeyboardButton(text="📃 Документация", url=settings.DOCS_URL)],
            [InlineKeyboardButton(text="📄 Логи о транзакциях", callback_data="logs")],
        ]
    )
