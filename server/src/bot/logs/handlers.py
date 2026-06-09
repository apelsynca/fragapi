from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.types import User as TGUser
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.helper import get_some_user
from src.models import User
from src.telegram_log.service import telegram_log as telegram_log_service

router = Router(name="telegram_logs")


class TelegramLogsForm(StatesGroup):
    target = State()


LOGS_STATUS_SETUP_TEXT = "✅ <b>Настроено</b>\nChatID: {chat_id}"
STATUS_STATUS_UNSET_TEXT = "❄️ <b>Не настроено</b>"

INFO_ABOUT_LOGS = "Информация о настройке логов о транзакциях:\n\n{status}"


async def get_logs_info(
    session: AsyncSession, user: User
) -> tuple[str, InlineKeyboardMarkup]:
    logs_sources = await telegram_log_service.get_all_sources(
        session=session, user=user
    )

    if len(logs_sources) > 0:
        logs_source = logs_sources[0]
        status_text = LOGS_STATUS_SETUP_TEXT.format(logs_source.chat_id)
    else:
        status_text = STATUS_STATUS_UNSET_TEXT

    text = INFO_ABOUT_LOGS.format(status=status_text)
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Настроить чат", callback_data="set_logs_target"
                )
            ]
        ]
    )

    return text, reply_markup


@router.callback_query(F.data == "logs")
async def get_logs_info_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_some_user(session=session, tg_user=callback.from_user)
    text, reply_markup = await get_logs_info(session=session, user=user)

    await callback.answer()
    await cast(Message, callback.message).edit_text(
        text=text, reply_markup=reply_markup
    )


GIVE_CHAT_ID_TEXT = (
    "✍️ <b>Введите/Выберите chat_id telegram чата в который должны будут приходить логи</b>\n\n"
    "<blockquote>\n"
    "Что такое chat_id? - Айди чата/канала телеграм\n"
    "Как его узнать? - Перешлите сообщение из чата/канала в @userinfobot и скопируйте цифры"
    "</blockquote>\n\n"
    "<i>Или выберите снизу</i> 👇"
)


@router.callback_query(F.data == "set_logs_target")
async def set_logs_target(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TelegramLogsForm.target)
    await cast(Message, callback.message).edit_text(
        text=GIVE_CHAT_ID_TEXT,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Логи в этот чат", callback_data="target_this_chat"
                    )
                ]
            ]
        ),
    )


@router.message(TelegramLogsForm.target)
async def on_logs_target_changed(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    if message.text is None:
        await message.answer(
            text="Enter text lol", reply_to_message_id=message.message_id
        )
        return

    user = await get_some_user(session=session, tg_user=cast(TGUser, message.from_user))
    await telegram_log_service.set_source(
        session=session, user=user, chat_id=message.text
    )

    await state.clear()
    await message.edit_text(text="Changed target to a new one!")
    await message.answer(text="123", reply_to_message_id=message.message_id)


@router.callback_query(F.data == "target_this_chat")
async def set_logs_target_as_this_chat(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    message = cast(Message, callback.message)
    user = await get_some_user(session=session, tg_user=callback.from_user)

    await state.clear()
    await telegram_log_service.set_source(
        session=session, user=user, chat_id=message.chat.id
    )

    await callback.answer(
        "Логи о транзакциях будут приходить в этот чат (от бота)", show_alert=True
    )

    text, reply_markup = await get_logs_info(session=session, user=user)
    await message.edit_text(text=text, reply_markup=reply_markup)
