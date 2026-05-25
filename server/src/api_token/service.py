from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_token.schemas import ApiTokenCreate
from src.exceptions import BadRequest, ResourceNotFound
from src.kit.utils import utc_now
from src.models.api_tokens import ApiToken
from src.models.users import User


class ApiTokenService:
    async def get_by_user(
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

        return api_token

    async def delete(self, session: AsyncSession, user: User, id: UUID) -> None:
        api_token = await session.scalar(select(ApiToken).where(ApiToken.id == id))

        if api_token is None:
            raise ResourceNotFound()

        if api_token.user_id != user.id:
            raise ResourceNotFound()

        await session.delete(api_token)


api_token = ApiTokenService()
