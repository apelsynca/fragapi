from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.models import AuthSubject
from src.auth.scope import Scope
from src.models import User

_PremiumGlobal = Authenticator(required_scopes={Scope.premium}, allowed_subjects={User})

PremiumGlobal = Annotated[AuthSubject[User], Depends(_PremiumGlobal)]
