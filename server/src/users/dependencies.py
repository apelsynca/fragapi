from typing import Annotated

from fastapi import Depends

from src.database.dependencies import DBSession

from .repository import UserRepository
from .service import UserService


async def get_user_service(session: DBSession) -> UserService:
    repository = UserRepository(session=session)
    return UserService(repository=repository)


UserServiceDependency = Annotated[UserService, Depends(get_user_service)]
