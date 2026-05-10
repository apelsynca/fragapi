from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.models import AuthSubject
from src.auth.scope import Scope
from src.models import User

_StarsBuy = Authenticator(required_scopes={Scope.stars_buy}, allowed_subjects={User})

StarsBuy = Annotated[AuthSubject[User], Depends(_StarsBuy)]
