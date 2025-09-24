from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .manager import session_manager


async def get_db_session(request: Request):
    if session := getattr(request.state, "session", None):
        yield session
    else:
        async with session_manager.session() as session:
            request.state.session = session
            yield session


DBSession = Annotated[AsyncSession, Depends(get_db_session)]
