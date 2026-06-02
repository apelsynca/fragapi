from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.postgres import AsyncSession, get_db_session
from src.routing import APIRouter

router = APIRouter(tags=["health"], include_in_schema=False)


@router.get("/health")
async def healthz(session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    try:
        await session.execute(select(1))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="Database is not available") from e

    return {"status": "ok"}
