from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.models import AuthSubject
from src.auth.scope import Scope
from src.models import User

_ApiTokensRead = Authenticator(
    required_scopes={Scope.api_tokens_read}, allowed_subjects={User}
)

ApiTokensRead = Annotated[AuthSubject[User], Depends(_ApiTokensRead)]
