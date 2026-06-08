from aiogram import Dispatcher

from src.bot.menu.handlers import router as menu_router

dispatcher = Dispatcher()

dispatcher.include_router(menu_router)
