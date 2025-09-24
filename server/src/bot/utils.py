from collections.abc import Callable, Coroutine
from typing import Any

from telegram import Update

from src.database import session_manager


def with_session(func) -> Callable[[Update, Any], Coroutine[Any, Any, Any]]:
    async def wrapper(update: Update, context):
        async with session_manager.session() as session:
            return await func(update, context, session)

    return wrapper
