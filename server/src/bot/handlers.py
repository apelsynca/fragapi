from aiogram import Dispatcher

from src.menu.router import router as menu_router

dispatcher = Dispatcher()

dispatcher.include_router(menu_router)
