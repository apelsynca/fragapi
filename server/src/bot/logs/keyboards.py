from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Настроить чат", callback_data="set_logs_target"
                )
            ]
        ]
    )


def get_select_target_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Логи в этот чат", callback_data="target_this_chat"
                )
            ]
        ]
    )
