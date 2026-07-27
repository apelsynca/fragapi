import structlog
from fastapi import Request
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import selectinload

from src.auth.schemas import LoginResponse
from src.exceptions import ResourceNotFound
from src.kit.crypto import generate_token
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import ApiToken, User, UserSession
from src.models.user_sessions import USER_SESSION_PREFIX
from src.postgres import AsyncSession

log: Logger = structlog.get_logger()


class AuthService:
    async def login_by_bot_hash(
        self, session: AsyncSession, bot_hash: str, *, request: Request | None = None
    ) -> LoginResponse:
        stmt = select(UserSession).where(
            # WARN: expires_at somehow not checking
            UserSession.bot_hash == bot_hash,
            UserSession.expires_at > utc_now(),
        )
        user_session = await session.scalar(stmt)

        if user_session is None:
            raise ResourceNotFound()

        user_agent = None
        if request is not None:
            user_agent = request.headers.get("user-agent")

        new_us = UserSession(
            user=user_session.user,
            user_agent=user_agent,
            token=generate_token(prefix=USER_SESSION_PREFIX),
        )
        session.add(new_us)
        await session.flush()
        await session.delete(user_session)

        return LoginResponse(token=new_us.token, success=True)

    async def authenticate(
        self, session: AsyncSession, session_token: str
    ) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession.token == session_token, UserSession.expires_at > utc_now()
        )
        return await session.scalar(stmt)

    async def authenticate_by_api_token(
        self, session: AsyncSession, token: str
    ) -> User | None:
        api_token = await session.scalar(
            select(ApiToken)
            .where(
                ApiToken.token == token,
                or_(ApiToken.expires_at > utc_now(), ApiToken.expires_at.is_(None)),
            )
            .options(selectinload(ApiToken.user))
        )

        if api_token is not None:
            return api_token.user

    async def delete_expired(self, session: AsyncSession) -> None:
        statement = delete(UserSession).where(UserSession.expires_at < utc_now())
        await session.execute(statement)


auth = AuthService()
