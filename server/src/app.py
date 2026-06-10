from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypedDict

import structlog
from aiogram import Bot
from fastapi import FastAPI
from fastapi.routing import APIRoute

from src import rate_limit
from src.api import router
from src.auth.middlewares import AuthSubjectMiddleware
from src.bot import create_bot
from src.bot.endpoints import router as bot_router
from src.bot.webhook import setup_webhook
from src.config import settings
from src.exception_handlers import add_exception_handlers
from src.health.endpoints import router as health_router
from src.integrations.fragment import Fragment
from src.integrations.fragment.rest_client import FragmentRestClient
from src.kit.database.postgres import (
    AsyncEngine,
    AsyncSessionMaker,
    create_async_sessionmaker,
)
from src.kit.ton_connect import TonConnect
from src.logging import Logger
from src.logging import configure as configure_logging
from src.middlewares import (
    KiqEnqueuedTasksMiddleware,
    LogTraceIdMiddleware,
    SandboxResponseHeaderMiddleware,
)
from src.openapi import OPENAPI_PARAMETERS, APITag, set_openapi_generator
from src.postgres import AsyncSessionMiddleware, create_async_engine
from src.wallet.ton import create_wallet
from src.wallet.ton import toncenter as toncenter_client
from src.worker import broker

log: Logger = structlog.get_logger()


class State(TypedDict):
    async_engine: AsyncEngine
    async_sessionmaker: AsyncSessionMaker
    fragment: Fragment
    bot: Bot


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[State]:
    log.info("Starting FragAPI")

    async_engine = create_async_engine("app")
    async_sessionmaker = create_async_sessionmaker(async_engine)

    ton_connect = TonConnect.from_wallet(
        wallet=create_wallet(), tc_domain="fragment.com"
    )
    fragment_rest_client = FragmentRestClient(
        ton_connect=ton_connect,
        session_key="CanBeAnythingForNow",
    )
    await fragment_rest_client.ensure_authorized()
    fragment = Fragment(clients=[fragment_rest_client])

    bot = create_bot()
    if not settings.is_development():
        await setup_webhook(bot)  # does not work without VPN for me

    await broker.startup()

    log.info("FragAPI started")

    async with toncenter_client:
        yield State(
            async_engine=async_engine,
            async_sessionmaker=async_sessionmaker,
            fragment=fragment,
            bot=bot,
        )

    await broker.shutdown()

    if not settings.is_development():
        await bot.delete_webhook()

    log.info("FragAPI stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        generate_unique_id_function=generate_unique_openapi_id,
        lifespan=lifespan,
        **OPENAPI_PARAMETERS,
    )

    if not settings.is_testing():
        app.add_middleware(rate_limit.get_middleware)
        app.add_middleware(AuthSubjectMiddleware)
        app.add_middleware(AsyncSessionMiddleware)
        app.add_middleware(KiqEnqueuedTasksMiddleware)

    if settings.is_sandbox():
        app.add_middleware(SandboxResponseHeaderMiddleware)

    app.add_middleware(LogTraceIdMiddleware)

    add_exception_handlers(app)

    app.include_router(router)
    app.include_router(health_router)
    app.include_router(bot_router)

    set_openapi_generator(app)

    return app


def generate_unique_openapi_id(route: APIRoute) -> str:
    parts = [str(tag) for tag in route.tags if tag not in APITag] + [route.name]
    return ":".join(parts)


configure_logging(logtide_service="server")

app = create_app()
