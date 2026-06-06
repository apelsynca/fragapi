# import secrets
# from typing import cast
#
# import structlog
# from src.bot.utils.decorators import with_session
# from telegram import CallbackQuery, Message, Update
# from telegram import User as TGUser
# from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
#
# from src.bot.menu.keyboards import get_login_keyboard, get_menu_keyboard
# from src.exceptions import ResourceNotFound
# from src.kit.crypto import generate_token
# from src.logging import Logger
# from src.models.user_sessions import USER_SESSION_PREFIX, UserSession
# from src.models.users import User
# from src.postgres import AsyncSession
# from src.user.schemas import UserCreate
# from src.user.service import user as user_service
#
# LOGIN_ARG = "login"
#
# log: Logger = structlog.get_logger()
#
#
# @with_session
# async def menu(
#     update: Update, context: ContextTypes.DEFAULT_TYPE, session: AsyncSession
# ) -> None:
#     message = cast(Message, update.message)
#     e_user = cast(TGUser, update.effective_user)
#
#     try:
#         user = await user_service.get_by_id(session=session, id=e_user.id)
#     except ResourceNotFound:
#         user = await user_service.create(
#             session=session,
#             user=UserCreate(
#                 id=e_user.id,
#                 first_name=e_user.first_name,
#                 last_name=e_user.last_name,
#                 username=e_user.username,
#                 is_premium=e_user.is_premium or False,
#             ),
#         )
#
#     if context.args and context.args[0] == LOGIN_ARG:
#         return await login(update, user, session)
#
#     await message.reply_text(
#         text=f"Привет, <b>{e_user.full_name}</b>\n\nБаланс: <b>{user.balance:.2f} TON</b>",
#         reply_markup=get_menu_keyboard(),
#     )
#
#
# async def login(update: Update, user: User, session: AsyncSession) -> None:
#     message = cast(Message, update.message)
#
#     user_session = UserSession(
#         user=user,
#         user_agent=None,
#         token=generate_token(prefix=USER_SESSION_PREFIX),
#         bot_hash=secrets.token_urlsafe(24),
#     )
#
#     session.add(user_session)
#     await session.commit()
#     await session.refresh(user_session)
#
#     if user_session.bot_hash is None:
#         log.error("bot login handler somehow the bot hash is None")
#         return
#
#     await message.reply_text(
#         text="Авторизация прошла успешно!\n\nНажмите войти 👇",
#         reply_markup=get_login_keyboard(bot_hash=user_session.bot_hash),
#     )
#
#
# async def notifications_empty(update: Update, _) -> None:
#     cbq = cast(CallbackQuery, update.callback_query)
#
#     await cbq.answer(text="Coming soon...", show_alert=True)
#
#
# def setup_callbacks(application: Application):
#     application.add_handler(CommandHandler({"start", "menu"}, menu))
#     application.add_handler(
#         CallbackQueryHandler(callback=notifications_empty, pattern="^notifications$")
#     )
