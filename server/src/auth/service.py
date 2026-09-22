import structlog
from datetime import timedelta
from fastapi import Request
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import selectinload

from src.auth.schemas import LoginResponse
from src.config import settings
from src.exceptions import ResourceNotFound
from src.kit.crypto import generate_token
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import ApiToken, User, UserSession
from src.models.user_sessions import USER_SESSION_PREFIX
from src.postgres import AsyncSession

log: Logger = structlog.get_logger()


SESSION_REFRESH_THRESHOLD = timedelta(hours=1)


class AuthService:
    async def login_by_bot_hash(
        self, session: AsyncSession, bot_hash: str, *, request: Request | None = None
    ) -> LoginResponse:
        stmt = select(UserSession).where(
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
        user_session = await session.scalar(stmt)

        if user_session is not None:
            await self._maybe_slide_expiration(session, user_session)

        return user_session

    async def _maybe_slide_expiration(
        self, session: AsyncSession, user_session: UserSession
    ) -> None:
        """Sliding expiration, throttled: renew the TTL once the session has
        aged past SESSION_REFRESH_THRESHOLD, so active users are not logged
        out while idle sessions still expire on schedule."""
        now = utc_now()
        if (
            user_session.expires_at - now
            >= settings.USER_SESSION_TTL - SESSION_REFRESH_THRESHOLD
        ):
            return

        user_session.expires_at = now + settings.USER_SESSION_TTL
        await session.flush()

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
