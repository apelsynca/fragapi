from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.types import User as TGUser
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.helper import get_fresh_user_from_tg_user
from src.bot.logs import keyboards, texts
from src.models import User
from src.telegram_log.service import telegram_log as telegram_log_service

router = Router(name="telegram_logs")


class TelegramLogsForm(StatesGroup):
    target = State()


async def get_menu_info(
    session: AsyncSession, user: User
) -> tuple[str, InlineKeyboardMarkup]:
    logs_sources = await telegram_log_service.get_all_sources(
        session=session, user=user
    )

    if len(logs_sources) > 0:
        logs_source = logs_sources[0]
        status_text = texts.STATUS_SETTED_UP_SINGLE.format(chat_id=logs_source.chat_id)
    else:
        status_text = texts.STATUS_UNSET

    text = texts.INFO_ABOUT_LOGS.format(status=status_text)

    return text, keyboards.get_menu_keyboard()


@router.callback_query(F.data == "logs")
async def get_logs_info_inline(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_fresh_user_from_tg_user(
        session=session, tg_user=callback.from_user
    )
    text, reply_markup = await get_menu_info(session=session, user=user)

    await callback.answer()
    await cast(Message, callback.message).edit_text(
        text=text, reply_markup=reply_markup
    )


@router.callback_query(F.data == "set_logs_target")
async def set_logs_target(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TelegramLogsForm.target)
    await cast(Message, callback.message).edit_text(
        text=texts.GIVE_CHAT_ID,
        reply_markup=keyboards.get_select_target_keyboard(),
    )


@router.message(TelegramLogsForm.target)
async def on_logs_target_changed(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    if message.text is None:
        await message.answer(
            text=texts.NO_TEXT_WAS_ENTERED, reply_to_message_id=message.message_id
        )
        return

    user = await get_fresh_user_from_tg_user(
        session=session, tg_user=cast(TGUser, message.from_user)
    )
    await telegram_log_service.set_source(
        session=session, user=user, chat_id=message.text
    )

    await state.clear()
    msg = await message.answer(text=texts.CHANGED_TARGET_CHAT_ID)

    text, reply_markup = await get_menu_info(session=session, user=user)

    await msg.reply(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == "target_this_chat")
async def set_logs_target_as_this_chat(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    message = cast(Message, callback.message)
    user = await get_fresh_user_from_tg_user(
        session=session, tg_user=callback.from_user
    )

    await state.clear()
    await telegram_log_service.set_source(
        session=session, user=user, chat_id=message.chat.id
    )

    await callback.answer(text=texts.LOGS_WILL_BE_HERE, show_alert=True)

    text, reply_markup = await get_menu_info(session=session, user=user)
    await message.edit_text(text=text, reply_markup=reply_markup)
