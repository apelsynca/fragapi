# from telegram import InlineKeyboardButton, InlineKeyboardMarkup
#
# from src.config import settings
#
#
# def get_menu_keyboard() -> InlineKeyboardMarkup:
#     return InlineKeyboardMarkup(
#         [
#             [InlineKeyboardButton(text="🌐 Панель", url=settings.PANEL_URL)],
#             [InlineKeyboardButton(text="📃 Документация", url=settings.DOCS_URL)],
#             [
#                 InlineKeyboardButton(
#                     text="🔔 Уведомления", callback_data="notifications"
#                 )
#             ],
#         ]
#     )
#
#
# def get_login_keyboard(bot_hash: str) -> InlineKeyboardMarkup:
#     return InlineKeyboardMarkup(
#         [
#             [
#                 InlineKeyboardButton(
#                     text="Войти",
#                     url=f"{settings.PANEL_URL}/bot-login?hash={bot_hash}",
#                 )
#             ]
#         ]
#     )
