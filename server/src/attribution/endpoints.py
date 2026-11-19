from fastapi import Depends
from fastapi.responses import RedirectResponse

from src.attribution.schemas import Attribution
from src.attribution.service import create_start_argument
from src.config import settings
from src.openapi import APITag
from src.redis import Redis, get_redis
from src.routing import APIRouter

router = APIRouter(prefix="/attribution", tags=["attribution", APITag.private])


@router.get("/start")
async def start(
    attribution: Attribution = Depends(), redis: Redis = Depends(get_redis)
) -> RedirectResponse:
    argument = await create_start_argument(redis, attribution)
    return RedirectResponse(
        f"https://t.me/{settings.BOT_USERNAME}?start={argument}",
        status_code=302,
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )
