from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User

router = Router(name="telegram_logs")


class TelegramLogsForm(StatesGroup):
    target = State()


@router.callback_query(F.data == "logs")
async def get_logs_info(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    # get all logs targets, and thread it as 1 (will be only one anyway for now)

    await callback.answer()
    await cast(Message, callback.message).edit_text(text="Информация о логах")


@router.callback_query(F.data == "set_logs_target")
async def set_logs_target(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TelegramLogsForm.target)
    await cast(Message, callback.message).edit_text(
        text="Введите chat_id чата/канала в который должны будут приходить логи\n\nИли выберите снизу 👇🏻"
    )


@router.message(TelegramLogsForm.target)
async def on_logs_target_changed(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.edit_text(text="Changed target to a new one!")
    await message.answer(text="123", reply_to_message_id=message.message_id)
