from src.auth.dependencies import APIUser, WebUser
from src.database.dependencies import DBSession
from src.kit.utils import generate_api_key
from src.models import User
from src.openapi import APITag
from src.routing import APIRouter

from .schemas import PanelUserRead, RevokeTokenResponse, UserRead

router = APIRouter(prefix="/users", tags=["Users", APITag.documented])


@router.get("/me", response_model=UserRead)
async def get_api_user_me(user: APIUser) -> User:
    return user


panel_router = APIRouter(prefix="/panel/users", tags=["Users", "Panel", APITag.private])


@panel_router.get("/me", response_model=PanelUserRead)
async def get_user_me(user: WebUser) -> User:
    return user


@panel_router.post("/revoke_api_token")
async def revoke_api_token(user: WebUser, session: DBSession) -> RevokeTokenResponse:
    user.api_key = generate_api_key()
    await session.commit()

    return RevokeTokenResponse(success=True, api_key=user.api_key)
