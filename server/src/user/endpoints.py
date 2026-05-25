from src.auth.dependencies import AuthorizeAPIUser
from src.models import User
from src.openapi import APITag
from src.routing import APIRouter
from src.user import auth
from src.user.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users", APITag.public])


@router.get("/me", response_model=UserRead)
async def get_api_user_me(auth_subject: AuthorizeAPIUser) -> User:
    return auth_subject.subject


@router.get("/api-keys")
async def get_api_keys(auth_subject: auth.ReadApiKeys) -> list:
    return []
