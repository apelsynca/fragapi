from collections.abc import Sequence
from uuid import UUID

import structlog
from sqlalchemy import select

from src.api_token.schemas import ApiTokenCreate
from src.exceptions import BadRequest, ResourceNotFound
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import ApiToken, User
from src.postgres import AsyncSession

log: Logger = structlog.get_logger()


class ApiTokenService:
    async def get_all_by_user(
        self, session: AsyncSession, user: User
    ) -> Sequence[ApiToken]:
        stmt = select(ApiToken).where(ApiToken.user == user)
        result = await session.execute(stmt)

        return result.scalars().unique().all()

    async def create(
        self, session: AsyncSession, user: User, data: ApiTokenCreate
    ) -> ApiToken:
        now = utc_now()
        if data.expires_at is not None and data.expires_at <= now:
            raise BadRequest("Cannot create already expired token")

        api_token = ApiToken(user=user, name=data.name, expires_at=data.expires_at)
        session.add(api_token)
        await session.flush()

        return api_token

    async def delete(self, session: AsyncSession, user: User, id: UUID) -> None:
        api_token = await session.scalar(select(ApiToken).where(ApiToken.id == id))
        if api_token is None:
            raise ResourceNotFound()

        if api_token.user_id != user.id:
            log.info(
                "api_token.delete for a wrong user",
                id=id,
                user=user,
                api_token_user_id=api_token.user_id,
            )
            raise ResourceNotFound()

        await session.delete(api_token)


api_token = ApiTokenService()
