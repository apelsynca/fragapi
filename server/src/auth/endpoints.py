from fastapi import Request

from src.auth.dependencies import AuthServiceDependency
from src.exceptions import ResourceNotFound
from src.openapi import APITag
from src.routing import APIRouter
from src.users.dependencies import UserServiceDependency
from src.users.schemas import UserCreate

from .schemas import LoginResponse, TelegramAuthData, TelegramBotAuthData

router = APIRouter(prefix="/auth", tags=["Auth", APITag.private])


@router.post("/telegram")
async def telegram_auth(
    request: Request,
    data: TelegramAuthData,
    user_service: UserServiceDependency,
    auth_service: AuthServiceDependency,
) -> LoginResponse:
    try:
        user = await user_service.get(id=data.id)
    except ResourceNotFound:
        user = await user_service.create(UserCreate.model_validate(data))

    return await auth_service.login(
        user=user, user_agent=request.headers.get("User-Agent", None)
    )


@router.post("/tgbot")
async def telegram_bot_auth(
    data: TelegramBotAuthData, auth_service: AuthServiceDependency
) -> LoginResponse:
    return await auth_service.login_by_bot_hash(bot_hash=data.hash)
