from src.models import User
from src.openapi import APITag
from src.routing import APIRouter
from src.user import auth
from src.user.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users", APITag.public])


@router.get("/me", response_model=UserRead, description="Get info about your account")
async def get_api_user_me(auth_subject: auth.UserRead) -> User:
    return auth_subject.subject
