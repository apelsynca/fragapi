from aiogram import Bot
from aiogram.types import Update
from fastapi import Depends, Request, Response

from src.bot.handlers import dispatcher
from src.config import settings
from src.openapi import APITag
from src.postgres import AsyncSession, get_db_session
from src.routing import APIRouter

router = APIRouter(tags=[APITag.private])


@router.post(settings.BOT_WEBHOOK_PATH)
async def telegram_bot_webhook(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> Response:
    try:
        bot: Bot = request.state.bot
    except AttributeError:
        raise RuntimeError("Bot not in state, fixit")

    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dispatcher.feed_update(bot=bot, update=update, session=session)

    return Response(status_code=200)
