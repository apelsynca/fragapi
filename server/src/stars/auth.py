from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.models import AuthSubject
from src.auth.scope import Scope
from src.models import User

_StarsGlobal = Authenticator(required_scopes={Scope.stars}, allowed_subjects={User})

StarsGlobal = Annotated[AuthSubject[User], Depends(_StarsGlobal)]
