from collections.abc import Sequence

from fastapi import Depends
from pydantic import UUID4

from src.api_token import auth
from src.api_token.schemas import ApiToken as ApiTokenSchema
from src.api_token.schemas import ApiTokenCreate
from src.api_token.service import api_token as api_token_service
from src.models import ApiToken
from src.openapi import APITag
from src.postgres import AsyncSession, get_db_session
from src.routing import APIRouter

router = APIRouter(prefix="/api-tokens", tags=["api_tokens", APITag.private])


@router.get("", response_model=list[ApiTokenSchema], description="Get all API Tokens")
async def get_api_tokens(
    auth_subject: auth.ApiTokensRead, session: AsyncSession = Depends(get_db_session)
) -> Sequence[ApiToken]:
    return await api_token_service.get_all_by_user(
        session=session, user=auth_subject.subject
    )


@router.post("", response_model=ApiTokenSchema, description="Create API Token")
async def create_api_token(
    auth_subject: auth.ApiTokensRead,
    data: ApiTokenCreate,
    session: AsyncSession = Depends(get_db_session),
) -> ApiToken:
    return await api_token_service.create(
        session=session, user=auth_subject.subject, data=data
    )


@router.delete("/{id}", description="Delete API Token")
async def delete_api_token(
    id: UUID4,
    auth_subject: auth.ApiTokensRead,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    return await api_token_service.delete(
        session=session, user=auth_subject.subject, id=id
    )
