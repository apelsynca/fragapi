from fastapi.responses import RedirectResponse

from src.config import settings
from src.routing import APIRouter

router = APIRouter(include_in_schema=False)


@router.get("/")
async def redirect_to_panel():
    return RedirectResponse(url=settings.panel_url)
