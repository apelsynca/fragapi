from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError

from src.auth.repository import UserSessionRepository
from src.auth.service import AuthService
from src.database.dependencies import DBSession
from src.enums import Scope, UserRole
from src.exceptions import NotPermitted, ResourceNotFound, Unauthorized
from src.models import User, UserSession
from src.users.dependencies import UserServiceDependency


async def get_user_session_repository(session: DBSession) -> UserSessionRepository:
    return UserSessionRepository(session)


def get_auth_service(
    user_session_repository: UserSessionRepository = Depends(
        get_user_session_repository
    ),
) -> AuthService:
    return AuthService(session_repository=user_session_repository)


AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


_Bearer = HTTPBearer(
    scheme_name="User session",
    auto_error=False,
    description="JWT Token auth credentials",
)
Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(_Bearer)]

_APIBearer = HTTPBearer(
    scheme_name="API Token", auto_error=False, description="API Token from your panel"
)
APICredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(_APIBearer)]


async def get_user_session(
    credentials: Credentials,
    auth_service: AuthServiceDependency,
) -> UserSession | None:
    if credentials is None:
        raise Unauthorized("Missing HTTP Bearer")

    try:
        return await auth_service.authenticate(jwt_token=credentials.credentials)
    except ExpiredSignatureError:
        raise Unauthorized("Expired signature error")
    except Exception:
        raise Unauthorized("Unauthorized")


def get_user(user_session: UserSession | None = Depends(get_user_session)) -> User:
    if user_session is None:
        raise Unauthorized(message="No user session")
    return user_session.user


async def get_api_user(
    credentials: APICredentials, user_service: UserServiceDependency
) -> User:
    if credentials is None:
        raise Unauthorized("Missing HTTP Bearer API key")

    try:
        return await user_service.get_by_api_key(api_key=credentials.credentials)
    except ResourceNotFound:
        raise Unauthorized("Wrong API key")


class Authenticator:
    SCOPES_BY_ROLE = {
        UserRole.ADMIN: {Scope.USER, Scope.ADMIN},
        UserRole.USER: {Scope.USER},
    }

    def __init__(self, scopes: set[Scope]):
        self.scopes = frozenset(scopes)

    def has_allowed_role(self, role: UserRole) -> bool:
        role_scopes = self.SCOPES_BY_ROLE[role]

        for scope in self.scopes:
            if scope in role_scopes:
                return True

        return False


class WebAuthenticator(Authenticator):
    def __call__(self, user: User = Depends(get_user)) -> User:
        if self.has_allowed_role(role=user.role) is False:
            raise NotPermitted

        return user


class APIAuthenticator(Authenticator):
    def __call__(self, user: User = Depends(get_api_user)) -> User:
        if self.has_allowed_role(role=user.role) is False:
            raise NotPermitted

        return user


WebUserAuthenticator = WebAuthenticator(scopes={Scope.USER})
WebUser = Annotated[User, Depends(WebUserAuthenticator)]

ApiUserAuthenticator = APIAuthenticator(scopes={Scope.USER})
APIUser = Annotated[User, Depends(ApiUserAuthenticator)]
