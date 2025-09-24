from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.database.dependencies import DBSession
from src.routing import APIRouter

router = APIRouter(tags=["health"], include_in_schema=False)


@router.get("/health")
async def healthz(session: DBSession) -> dict[str, str]:
    try:
        await session.execute(select(1))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="Database is not available") from e

    return {"status": "ok"}
