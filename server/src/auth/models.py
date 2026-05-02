from typing import TypeGuard

from src.auth.scope import Scope
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


def is_anonymous[S: Subject](
    auth_subject: AuthSubject[S],
) -> TypeGuard[AuthSubject[Anonymous]]:
    return isinstance(auth_subject.subject, Anonymous)
