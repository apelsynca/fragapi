from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI
from fastapi.routing import APIRoute

from src.api import router
from src.bot.app import bot_application
from src.bot.endpoints import router as bot_router
from src.bot.setup import setup_bot
from src.config import settings
from src.exception_handlers import add_exception_handlers
from src.health.endpoints import router as health_router
from src.kit.database.postgres import (
    AsyncEngine,
    AsyncSessionMaker,
    create_async_sessionmaker,
)
from src.logging import configure as configure_logging
from src.logging import get_logger
from src.middlewares import LogCorrelationIdMiddleware
from src.openapi import OPENAPI_PARAMETERS, APITag, set_openapi_generator
from src.panel_redirect.endpoints import router as panel_redirect_router
from src.postgres import AsyncSessionMiddleware, create_async_engine
from src.ton_wallet import client as toncenter_client
from src.ton_wallet import wallet
from src.ton_wallet.endpoints import router as tonapi_router

log = get_logger()


class State(TypedDict):
    async_engine: AsyncEngine
    async_sessionmaker: AsyncSessionMaker


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator:
    log.info("Starting Fragment API")

    async with toncenter_client:
        await wallet.refresh()  # for TonConnect to have latest info

    async_engine = create_async_engine("app")
    async_sessionmaker = create_async_sessionmaker(async_engine)

    if settings.is_production():
        await setup_bot(bot_application)
        await bot_application.initialize()
        await bot_application.start()

    log.info("Fragment API started")

    yield State(async_engine=async_engine, async_sessionmaker=async_sessionmaker)

    await bot_application.stop()
    await bot_application.shutdown()

    await toncenter_client.close()

    log.info("Fragment API stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        generate_unique_id_function=generate_unique_openapi_id,
        lifespan=lifespan,
        **OPENAPI_PARAMETERS,
    )

    if not settings.is_testing():
        app.add_middleware(LogCorrelationIdMiddleware)
        app.add_middleware(AsyncSessionMiddleware)

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
