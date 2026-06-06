from aiogram import Router
from aiogram.types import Message

router = Router(name="menu")


@router.message()
async def echo_handler(message: Message) -> None:
    await message.reply(text=f"{message.text} = The reply!")
