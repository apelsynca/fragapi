from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import AuthorizeAPIUser, AuthorizeWebUser
from src.kit.utils import generate_api_key
from src.models import User
from src.openapi import APITag
from src.postgres import get_db_session
from src.routing import APIRouter

from .schemas import PanelUserRead, RevokeTokenResponse, UserRead

router = APIRouter(prefix="/users", tags=["Users", APITag.documented])


@router.get("/me", response_model=UserRead)
async def get_api_user_me(auth_subject: AuthorizeAPIUser) -> User:
    return auth_subject.subject


panel_router = APIRouter(prefix="/panel/users", tags=["Users", "Panel", APITag.private])


@panel_router.get("/me", response_model=PanelUserRead)
async def get_user_me(auth_subject: AuthorizeWebUser) -> User:
    return auth_subject.subject


@panel_router.post("/revoke_api_token")
async def revoke_api_token(
    auth_subject: AuthorizeWebUser, session: AsyncSession = Depends(get_db_session)
) -> RevokeTokenResponse:
    auth_subject.subject.api_key = generate_api_key()
    await session.commit()

    return RevokeTokenResponse(success=True, api_key=auth_subject.subject.api_key)
