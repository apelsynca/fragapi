from src.auth.tasks import auth_pissie_piss
from src.models import User
from src.openapi import APITag
from src.routing import APIRouter
from src.user import auth
from src.user.schemas import UserRead
from src.worker import enqueue_task

router = APIRouter(prefix="/users", tags=["users", APITag.public])


@router.get("/me", response_model=UserRead)
async def get_api_user_me(auth_subject: auth.UserRead) -> User:
    return auth_subject.subject


@router.get("/abc")
async def get_abc() -> dict:
    enqueue_task(auth_pissie_piss)
    return {"something": "else"}
