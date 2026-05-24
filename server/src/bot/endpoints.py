from fastapi import Request, Response
from telegram import Update

from src.config import settings
from src.openapi import APITag
from src.routing import APIRouter

router = APIRouter(tags=[APITag.private])


@router.post(settings.BOT_WEBHOOK_PATH)
async def bot_webhook(request: Request) -> Response:
    try:
        # any because the real type is fucked up
        application = request.state.bot_application
    except AttributeError as e:
        raise RuntimeError(
            "Session is not present in the request state. "
            "Did you forget to add AsyncSessionMiddleware?"
        ) from e

    update = Update.de_json(data=await request.json(), bot=application.bot)
    await application.process_update(update)

    return Response(status_code=200)
