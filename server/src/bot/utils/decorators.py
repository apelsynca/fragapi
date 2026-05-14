from collections.abc import Callable, Coroutine
from typing import Any

from telegram import Update

from src.kit.database.postgres import create_async_sessionmaker
from src.postgres import create_async_engine


def with_session(func) -> Callable[[Update, Any], Coroutine[Any, Any, Any]]:
    async def wrapper(update: Update, context):
        async_engine = create_async_engine("bot")
        async_sessionmaker = create_async_sessionmaker(async_engine)

        async with async_sessionmaker() as session:
            try:
                result = await func(update, context, session)
            except:
                await session.rollback()
                raise
            else:
                await session.commit()

            return result

    return wrapper
