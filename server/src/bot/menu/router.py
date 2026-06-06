from aiogram import Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name="menu")


@router.message()
async def echo_handler(message: Message) -> None:
    await message.reply(text=f"{message.text} = The reply!")


@router.message()
async def start_handler(message: Message, session: AsyncSession) -> None:
    await message.reply(text="Hiiii!!!!!!!")
