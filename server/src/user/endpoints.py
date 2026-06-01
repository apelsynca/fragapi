from src.models import User
from src.openapi import APITag
from src.routing import APIRouter
from src.user import auth
from src.user.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead, tags=[APITag.public])
async def get_api_user_me(auth_subject: auth.UserRead) -> User:
    return auth_subject.subject


@router.get("/api-keys", tags=[APITag.private])
async def get_api_keys(auth_subject: auth.ApiKeysRead) -> str:
    return auth_subject.subject.api_key
