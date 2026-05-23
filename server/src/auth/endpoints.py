from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginResponse, TelegramBotAuthData
from src.auth.service import auth as auth_service
from src.openapi import APITag
from src.postgres import get_db_session
from src.routing import APIRouter

router = APIRouter(prefix="/auth", tags=["auth", APITag.private])


@router.post("/tgbot")
async def telegram_bot_auth(
    data: TelegramBotAuthData,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    return await auth_service.login_by_bot_hash(
        session, bot_hash=data.hash, request=request
    )
