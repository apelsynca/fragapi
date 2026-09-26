import structlog
from aiogram import Bot
from aiogram.types import Update
from fastapi import Depends, Request, Response

from src.bot.dispatcher import dispatcher
from src.config import settings
from src.exceptions import Forbidden
from src.logging import Logger
from src.openapi import APITag
from src.postgres import AsyncSession, get_db_session
from src.routing import APIRouter

router = APIRouter(tags=[APITag.private])

log: Logger = structlog.get_logger()


@router.post(settings.BOT_WEBHOOK_PATH)
async def telegram_bot_webhook(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> Response:
    try:
        bot: Bot = request.state.bot
    except AttributeError:
        raise RuntimeError("Bot not in state, fixit")

    telegram_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if telegram_secret != settings.BOT_WEBHOOK_SECRET_TOKEN:
        log.warning("telegram bot webhook wrong secret token")
        raise Forbidden()

    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dispatcher.feed_update(bot=bot, update=update, session=session)

    return Response(status_code=200)
