from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.models import AuthSubject
from src.auth.scope import Scope
from src.models import User

_PremiumGlobal = Authenticator(
    required_scopes={Scope.read_api_keys}, allowed_subjects={User}
)

ReadApiKeys = Annotated[AuthSubject[User], Depends(_PremiumGlobal)]
