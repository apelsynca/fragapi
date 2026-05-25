import structlog
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginResponse
from src.exceptions import Forbidden
from src.kit.crypto import generate_token
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import User, UserSession
from src.models.user_sessions import USER_SESSION_PREFIX
from src.user.repository import UserRepository

log: Logger = structlog.get_logger()


class AuthService:
    async def login_by_bot_hash(
        self, session: AsyncSession, bot_hash: str, *, request: Request | None = None
    ) -> LoginResponse:
        stmt = select(UserSession).where(UserSession.bot_hash == bot_hash)
        user_session = await session.scalar(stmt)

        if user_session is None:
            raise Forbidden()

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
        self, session: AsyncSession, api_key: str
    ) -> User | None:
        repository = UserRepository.from_session(session)
        return await repository.get_by_api_key(api_key=api_key)


auth = AuthService()
