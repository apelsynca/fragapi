from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI
from fastapi.routing import APIRoute
from telegram.ext import Application as BotApplication
from tonutils.contracts import WalletV5R1

from src.api import router
from src.auth.middlewares import AuthSubjectMiddleware
from src.bot.app import get_application as get_bot_application
from src.bot.endpoints import router as bot_router
from src.bot.setup import setup_bot
from src.config import settings
from src.exception_handlers import add_exception_handlers
from src.fragment_rest import create_fragment_rest
from src.fragment_rest.rest import FragmentRest
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
from src.postgres import AsyncSessionMiddleware, create_async_engine
from src.ton import create_wallet
from src.ton import toncenter as toncenter_client

log = get_logger()


class State(TypedDict):
    async_engine: AsyncEngine
    async_sessionmaker: AsyncSessionMaker
    bot_application: BotApplication
    wallet: WalletV5R1
    fragment_rest: FragmentRest


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[State]:
    log.info("Starting Fragment API")

    async_engine = create_async_engine("app")
    async_sessionmaker = create_async_sessionmaker(async_engine)

    bot_application = get_bot_application()

    if settings.is_production():
        await setup_bot(bot_application)
        await bot_application.initialize()
        await bot_application.start()

    wallet = create_wallet()
    fragment_rest = create_fragment_rest(wallet)

    await fragment_rest.start()

    log.info("Fragment API started")

    await toncenter_client.connect()

    yield State(
        async_engine=async_engine,
        async_sessionmaker=async_sessionmaker,
        bot_application=bot_application,
        wallet=wallet,
        fragment_rest=fragment_rest,
    )

    await toncenter_client.close()

    await bot_application.stop()
    await bot_application.shutdown()

    log.info("Fragment API stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        generate_unique_id_function=generate_unique_openapi_id,
        lifespan=lifespan,
        **OPENAPI_PARAMETERS,
    )

    if not settings.is_testing():
        app.add_middleware(AuthSubjectMiddleware)
        app.add_middleware(AsyncSessionMiddleware)
    app.add_middleware(LogCorrelationIdMiddleware)

    add_exception_handlers(app)

    app.include_router(router)
    # app.include_router(tonapi_router)
    app.include_router(health_router)
    app.include_router(bot_router)

    return app


def generate_unique_openapi_id(route: APIRoute) -> str:
    parts = [str(tag) for tag in route.tags if tag not in APITag] + [route.name]
    return ":".join(parts)


configure_logging()

app = create_app()
set_openapi_generator(app)
