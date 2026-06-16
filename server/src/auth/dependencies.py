from collections.abc import Awaitable, Callable
from inspect import Parameter, Signature
from typing import Annotated, Any

from fastapi import Depends, Request, Security
from fastapi.security import HTTPBearer
from makefun import with_signature

from src.auth.exceptions import InsufficientScopeError
from src.auth.models import Anonymous, AuthSubject, Subject, SubjectType, is_anonymous
from src.auth.scope import Scope
from src.exceptions import Unauthorized
from src.models import User

session_scheme = HTTPBearer(
    scheme_name="user_session",
    auto_error=False,
    description="User session scheme",
)

api_token_scheme = HTTPBearer(
    scheme_name="api_token", auto_error=False, description="API Token from your panel"
)

_auth_subject_factory_cache: dict[
    frozenset[SubjectType], Callable[..., Awaitable[AuthSubject[Subject]]]
] = {}


def _get_auth_subject_factory(
    allowed_subjects: frozenset[SubjectType],
) -> Callable[..., Awaitable[AuthSubject[Subject]]]:
    if allowed_subjects in _auth_subject_factory_cache:
        return _auth_subject_factory_cache[allowed_subjects]

    parameters: list[Parameter] = [
        Parameter(
            name="request",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Request,
        )
    ]

    if User in allowed_subjects:
        parameters += [
            Parameter(
                name="user_session_credentials",
                kind=Parameter.KEYWORD_ONLY,
                default=Depends(session_scheme),
            ),
            Parameter(
                name="api_token_credentials",
                kind=Parameter.KEYWORD_ONLY,
                default=Depends(api_token_scheme),
            ),
        ]

    signature = Signature(parameters)

    @with_signature(signature)
    async def get_auth_subject(request: Request, **kwargs: Any) -> AuthSubject[Subject]:
        try:
            return request.state.auth_subject
        except AttributeError as e:
            raise RuntimeError(
                "AuthSubject is not present in the request state. "
                "Did you forget to add AuthSubjectMiddleware?"
            ) from e

    _auth_subject_factory_cache[allowed_subjects] = get_auth_subject

    return get_auth_subject


class _Authenticator:
    def __init__(
        self,
        *,
        allowed_subjects: frozenset[SubjectType],
        required_scopes: set[Scope] | None = None,
    ) -> None:
        self.allowed_subjects = allowed_subjects
        self.required_scopes = required_scopes

    async def __call__(
        self, auth_subject: AuthSubject[Subject]
    ) -> AuthSubject[Subject]:
        subject_type = type(auth_subject.subject)
        if subject_type not in self.allowed_subjects:
            auth_subject = AuthSubject(Anonymous(), set(), None)

        # Anon
        if is_anonymous(auth_subject):
            if Anonymous in self.allowed_subjects:
                return auth_subject  # pyright: ignore[reportReturnType]
            else:
                raise Unauthorized()

        # No required scopes
        if not self.required_scopes:
            return auth_subject

        if auth_subject.scopes & self.required_scopes:
            return auth_subject

        raise InsufficientScopeError(f"{[s for s in self.required_scopes]}")


def Authenticator(
    allowed_subjects: set[SubjectType], required_scopes: set[Scope] | None = None
) -> _Authenticator:
    allowed_subjects_frozen = frozenset(allowed_subjects)

    parameters: list[Parameter] = [
        Parameter(name="self", kind=Parameter.POSITIONAL_OR_KEYWORD),
        Parameter(
            name="auth_subject",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            default=Security(
                _get_auth_subject_factory(allowed_subjects_frozen),
                scopes=sorted(s.value for s in (required_scopes or {})),
            ),
        ),
    ]
    signature = Signature(parameters)

    class _AuthenticatorSignature(_Authenticator):
        @with_signature(signature)
        async def __call__(
            self, auth_subject: AuthSubject[Subject]
        ) -> AuthSubject[Subject]:
            return await super().__call__(auth_subject)

    return _AuthenticatorSignature(
        allowed_subjects=allowed_subjects_frozen, required_scopes=required_scopes
    )


AuthorizeAPIUser = Annotated[
    AuthSubject[User],
    Depends(Authenticator(allowed_subjects={User}, required_scopes={Scope.api})),
]

AuthorizeWebUser = Annotated[
    AuthSubject[User],
    Depends(Authenticator(allowed_subjects={User}, required_scopes={Scope.web})),
]
