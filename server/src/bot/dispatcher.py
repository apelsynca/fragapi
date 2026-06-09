from aiogram import Dispatcher

from src.bot.logs.handlers import router as logs_router
from src.bot.menu.handlers import router as menu_router

dispatcher = Dispatcher()

dispatcher.include_router(menu_router)
dispatcher.include_router(logs_router)
