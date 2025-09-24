from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from src.auth.repository import UserSessionRepository
from src.auth.schemas import LoginResponse
from src.exceptions import AppError
from src.kit.jwt import decode_token, encode_token
from src.kit.utils import generate_api_key, utc_now
from src.logging import get_logger
from src.models import User, UserSession

log = get_logger()


class AuthService:
    def __init__(self, session_repository: UserSessionRepository):
        self.session_repository = session_repository

    async def login(
        self, user: User, user_agent: str | None = None, with_bot_hash: bool = False
    ) -> LoginResponse:
        try:
            token = encode_token(id=user.id, name=user.first_name)
            bot_hash = None
            if with_bot_hash:
                bot_hash = generate_api_key()

            try:
                user_session = await self.session_repository.create(
                    UserSession(
                        token=token, user_agent=user_agent, user=user, bot_hash=bot_hash
                    )
                )
            except IntegrityError:
                user_session = await self.session_repository.get_one_or_none(
                    select(UserSession).where(UserSession.token == token)
                )
                if user_session is None:
                    raise AppError("Cannot find session that's already created")

            if with_bot_hash and user_session.bot_hash is None:
                user_session = await self.session_repository.update(
                    user_session, {"bot_hash": bot_hash}
                )

            log.info(
                "User logged in",
                id=user.id,
                first_name=user.first_name,
                username=user.username,
            )

            return LoginResponse(
                token=token, success=True, bot_hash=user_session.bot_hash
            )
        except Exception as exc:
            log.warning("Error logging in", error=exc)
            return LoginResponse(token=None, success=False)

    async def authenticate(self, jwt_token: str) -> UserSession | None:
        payload = decode_token(token=jwt_token)

        stmt = (
            self.session_repository.get_base_stmt()
            .where(
                UserSession.user_id == payload.user_id,
                UserSession.token == jwt_token,
                UserSession.expires_at > utc_now(),
            )
            .options(joinedload(UserSession.user))
        )

        return await self.session_repository.get_one_or_none(stmt=stmt)

    async def login_by_bot_hash(self, bot_hash: str) -> LoginResponse:
        user_session = await self.session_repository.get_one_or_none(
            stmt=self.session_repository.get_base_stmt().where(
                UserSession.bot_hash == bot_hash
            )
        )

        if user_session:
            await self.session_repository.update(user_session, {"bot_hash": None})
            return LoginResponse(token=user_session.token, success=True)
        else:
            return LoginResponse(token=None, success=False)
