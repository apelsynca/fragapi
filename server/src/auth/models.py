from functools import cached_property
from typing import TypeGuard

from src.auth.scope import Scope
from src.enums import RateLimitGroup
from src.models import User, UserSession


class Anonymous: ...


Subject = User | Anonymous
SubjectType = type[User] | type[Anonymous]


class AuthSubject[S]:
    subject: S
    scopes: set[Scope]
    session: UserSession | None

    def __init__(
        self, subject: S, scopes: set[Scope], session: UserSession | None
    ) -> None:
        self.subject = subject
        self.scopes = scopes
        self.session = session

    @cached_property
    def rate_limit_key(self) -> tuple[str, RateLimitGroup]:
        return self.rate_limit_user, self.rate_limit_group

    @cached_property
    def rate_limit_user(self) -> str:
        match self.subject:
            case User():
                return f"user:{self.subject.id}"
            case Anonymous():
                return "anonymous"
        raise  # JIC

    @cached_property
    def rate_limit_group(self) -> RateLimitGroup:
        if isinstance(self.session, UserSession):
            return RateLimitGroup.web

        return RateLimitGroup.default

    @cached_property
    def log_context(self) -> dict[str, str]:
        baggage: dict[str, str] = {
            "subject_type": self.subject.__class__.__name__,
        }
        if isinstance(self.subject, User):
            baggage["subject_id"] = str(self.subject.id)

        if self.session:
            baggage["session_type"] = self.session.__class__.__name__

        return baggage


def is_anonymous[S: Subject](
    auth_subject: AuthSubject[S],
) -> TypeGuard[AuthSubject[Anonymous]]:
    return isinstance(auth_subject.subject, Anonymous)
