from fastapi import Request, Response
from telegram import Update

from src.bot.app import bot_application
from src.config import settings
from src.openapi import APITag
from src.routing import APIRouter

router = APIRouter(tags=[APITag.private])


@router.post(settings.bot.webhook_path)
async def bot_webhook(request: Request) -> Response:
    await bot_application.update_queue.put(
        Update.de_json(data=await request.json(), bot=bot_application.bot)
    )
    return Response(status_code=200)
