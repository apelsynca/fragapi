from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.models import AuthSubject
from src.auth.scope import Scope
from src.models import User

_TransactionsRead = Authenticator(
    required_scopes={Scope.transactions_read},
    allowed_subjects={User},
)


TransactionsRead = Annotated[AuthSubject[User], Depends(_TransactionsRead)]
