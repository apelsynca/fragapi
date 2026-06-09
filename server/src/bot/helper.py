from aiogram.types import User as TGUser
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import ResourceNotFound
from src.models import User
from src.user.service import user as user_service

# PERF: refactor this later


async def get_fresh_user_from_tg_user(session: AsyncSession, tg_user: TGUser) -> User:
    try:
        user = await user_service.get_by_id(session=session, id=tg_user.id)
        return await user_service.update_by_tg_user(
            session=session, user=user, tg_user=tg_user
        )
    except ResourceNotFound:
        return await user_service.create_from_tg_user(session=session, tg_user=tg_user)
