from typing import Any, Literal

import pytest

from src.auth.models import Anonymous, AuthSubject, Subject
from src.auth.scope import Scope
from src.models import User


class AuthSubjectFixture:
    def __init__(
        self,
        *,
        subject: Literal["anonymous", "user"] = "user",
        scopes: set[Scope] = set(Scope),
    ) -> None:
        self.subject = subject
        self.scopes = scopes

    def __repr__(self) -> str:
        scopes = (
            "{" + ", ".join(repr(scope.value) for scope in sorted(self.scopes)) + "}"
        )
        return f"AuthSubjectFixture(subject={self.subject!r}, scopes={scopes})"


@pytest.fixture
def auth_subject(
    request: pytest.FixtureRequest,
    user: User,
) -> AuthSubject[Subject]:
    user_auth_fixture: AuthSubjectFixture = request.param
    subject_key = user_auth_fixture.subject

    subjects_map = {"anonymous": Anonymous(), "user": user}
    subject = subjects_map[subject_key]

    session: Any = None
    if isinstance(subject, User):
        from unittest.mock import MagicMock

        from src.models import UserSession

        session = MagicMock(spec=UserSession)

    return AuthSubject(subject, user_auth_fixture.scopes, session)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "auth_subject" in metafunc.fixturenames:
        pytest_params = []

        # The test is decorated with the `auth` marker
        auth_marker = metafunc.definition.get_closest_marker("auth")
        if auth_marker is not None:
            args: tuple[Any, ...] = auth_marker.args
            if len(args) == 0:
                args = (AuthSubjectFixture(),)

            # Generate a test for each AuthSubjectFixture argument
            for arg in args:
                if not isinstance(arg, AuthSubjectFixture):
                    raise ValueError(
                        "auth marker arguments must be "
                        f"of type UserAuthFixture, got {type(arg)}"
                    )
                pytest_params.append(pytest.param(arg, id=repr(arg)))
        else:
            pytest_params = [
                pytest.param(AuthSubjectFixture(subject="anonymous"), id="anonymous")
            ]

        metafunc.parametrize("auth_subject", pytest_params, indirect=["auth_subject"])
