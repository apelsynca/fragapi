from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI
from fastapi.routing import APIRoute
from telegram.ext import Application as BotApplication

from src.api import router
from src.auth.middlewares import AuthSubjectMiddleware
from src.bot import get_bot_application, setup_bot
from src.bot.endpoints import router as bot_router
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
from src.logging import configure as configure_logging
from src.logging import get_logger
from src.middlewares import LogCorrelationIdMiddleware
from src.openapi import OPENAPI_PARAMETERS, APITag, set_openapi_generator
from src.postgres import AsyncSessionMiddleware, create_async_engine
from src.wallet.manager import WalletManager
from src.wallet.ton import create_wallet
from src.wallet.ton import toncenter as toncenter_client
from src.worker import broker

log = get_logger()


class State(TypedDict):
    async_engine: AsyncEngine
    async_sessionmaker: AsyncSessionMaker
    bot_application: BotApplication
    fragment: Fragment
    wallet_manager: WalletManager


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[State]:
    log.info("Starting Fragment API")

    async_engine = create_async_engine("app")
    async_sessionmaker = create_async_sessionmaker(async_engine)

    wallet = create_wallet()
    wallet_manager = WalletManager(ton_wallets=[wallet])

    fragment_rest_client = FragmentRestClient(
        ton_connect=TonConnect(wallet=wallet, tc_domain="fragment.com"),
        session_key="anyfornow",
    )
    await fragment_rest_client.ensure_authorized()
    fragment = Fragment(clients=[fragment_rest_client])

    bot_application = get_bot_application()
    if settings.is_production():
        await setup_bot(bot_application)
        await bot_application.initialize()
        await bot_application.start()

    await broker.startup()

    log.info("Fragment API started")

    async with toncenter_client:
        yield State(
            async_engine=async_engine,
            async_sessionmaker=async_sessionmaker,
            bot_application=bot_application,
            fragment=fragment,
            wallet_manager=wallet_manager,
        )

    await broker.shutdown()

    if settings.is_production():
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
        # i disable rate limiting for now, since requests from the web come from the server
        # app.add_middleware(rate_limit.get_middleware)
        app.add_middleware(AuthSubjectMiddleware)
        app.add_middleware(AsyncSessionMiddleware)
    app.add_middleware(LogCorrelationIdMiddleware)

    add_exception_handlers(app)

    app.include_router(router)
    app.include_router(health_router)
    app.include_router(bot_router)

    return app


def generate_unique_openapi_id(route: APIRoute) -> str:
    parts = [str(tag) for tag in route.tags if tag not in APITag] + [route.name]
    return ":".join(parts)


configure_logging()

app = create_app()
set_openapi_generator(app)
