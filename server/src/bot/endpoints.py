from aiogram.types import Update
from fastapi import Request, Response

from src.bot.handlers import dispatcher
from src.config import settings
from src.openapi import APITag
from src.routing import APIRouter

router = APIRouter(tags=[APITag.private])


@router.post(settings.BOT_WEBHOOK_PATH)
async def telegram_bot_webhook(request: Request) -> Response:
    try:
        bot = request.state.bot
    except AttributeError:
        raise RuntimeError("Bot not in state, fixit")

    update = Update.model_validate(await request.json())
    await dispatcher.feed_update(bot=bot, update=update)

    return Response(status_code=200)
