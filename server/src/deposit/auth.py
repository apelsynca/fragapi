from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.models import AuthSubject
from src.auth.scope import Scope
from src.models import User

_DepositRequest = Authenticator(
    required_scopes={Scope.deposit}, allowed_subjects={User}
)

DepositRequest = Annotated[AuthSubject[User], Depends(_DepositRequest)]
