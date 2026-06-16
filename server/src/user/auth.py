from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.models import AuthSubject
from src.auth.scope import Scope
from src.models import User

_UserRead = Authenticator(required_scopes={Scope.read_user}, allowed_subjects={User})

UserRead = Annotated[AuthSubject[User], Depends(_UserRead)]
