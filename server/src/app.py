from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute

from src.api import router
from src.bot.app import bot_application
from src.bot.endpoints import router as bot_router
from src.bot.setup import setup_bot
from src.database import session_manager
from src.exception_handlers import add_exception_handlers
from src.health.endpoints import router as health_router
from src.logging import configure as configure_logging
from src.logging import get_logger
from src.middlewares import LogCorrelationIdMiddleware
from src.openapi import OPENAPI_PARAMETERS, APITag, set_openapi_generator
from src.panel_redirect.endpoints import router as panel_redirect_router
from src.ton_wallet.endpoints import router as tonapi_router

log = get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator:
    log.info("Starting Fragment API")

    async with session_manager.connect() as conn:
        await session_manager.create_all(conn)

    await setup_bot(bot_application)

    await bot_application.initialize()
    await bot_application.start()

    log.info("Fragment API started")

    yield

    await bot_application.stop()
    await bot_application.shutdown()

    if session_manager._engine is not None:
        await session_manager.close()

    log.info("Fragment API stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        generate_unique_id_function=generate_unique_openapi_id,
        lifespan=lifespan,
        **OPENAPI_PARAMETERS,
    )

    app.add_middleware(LogCorrelationIdMiddleware)

    add_exception_handlers(app)

    app.include_router(router)
    app.include_router(tonapi_router)
    app.include_router(health_router)
    app.include_router(panel_redirect_router)
    app.include_router(bot_router)

    return app


def generate_unique_openapi_id(route: APIRoute) -> str:
    parts = [str(tag) for tag in route.tags if tag not in APITag] + [route.name]
    return ":".join(parts)


configure_logging()

app = create_app()
set_openapi_generator(app)
