import structlog
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from starlette.types import ASGIApp, Receive, Send
from starlette.types import Scope as ASGIScope

from src.auth.models import Anonymous, AuthSubject, Subject
from src.auth.scope import Scope
from src.auth.service import auth as auth_service
from src.logging import Logger
from src.models.user_sessions import USER_SESSION_PREFIX
from src.postgres import AsyncSession

log: Logger = structlog.get_logger()


def get_bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    scheme, value = get_authorization_scheme_param(authorization)
    if not scheme or not value or scheme.lower() != "bearer":
        return None
    if not value.isascii():
        return None
    return value


async def get_auth_subject(
    request: Request, session: AsyncSession
) -> AuthSubject[Subject]:
    # PERF: Scope admin ignored for now (refactorable lol)

    token = get_bearer_token(request)

    if token is not None:
        if token.startswith(USER_SESSION_PREFIX):
            user_session = await auth_service.authenticate(session, session_token=token)
            if user_session is not None:
                return AuthSubject(
                    user_session.user,
                    {
                        Scope.web,
                        Scope.transactions_read,
                        Scope.ton_rate_read,
                        Scope.api_tokens_read,
                        Scope.read_user,
                        Scope.deposit,
                    },
                    user_session,
                )
        user = await auth_service.authenticate_by_api_token(session, token=token)
        if user is not None:
            return AuthSubject(
                user,
                {
                    Scope.api,
                    Scope.transactions_read,
                    Scope.stars,
                    Scope.premium,
                    Scope.ton_rate_read,
                    Scope.read_user,
                    Scope.deposit,
                },
                None,
            )

    return AuthSubject(Anonymous(), set(), None)


class AuthSubjectMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: ASGIScope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        session: AsyncSession = scope["state"]["async_session"]
        request = Request(scope)

        auth_subject = await get_auth_subject(request, session)

        scope["state"]["auth_subject"] = auth_subject

        log.info("Authenticated subject", **auth_subject.log_context)
        await self.app(scope, receive, send)
