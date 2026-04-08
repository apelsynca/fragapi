from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres import get_db_session

from .repository import UserRepository
from .service import UserService


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    repository = UserRepository(session=session)
    return UserService(repository=repository)


UserServiceDependency = Annotated[UserService, Depends(get_user_service)]
