from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginResponse
from src.kit.utils import utc_now
from src.logging import get_logger
from src.models import User, UserSession
from src.users.repository import UserRepository

log = get_logger()


class AuthService:
    async def login_by_bot_hash(
        self, session: AsyncSession, bot_hash: str
    ) -> LoginResponse:
        stmt = select(UserSession).where(UserSession.bot_hash == bot_hash)
        user_session = await session.scalar(stmt)

        if user_session is None:
            raise

        return LoginResponse(token=user_session.token, success=True)

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
