from typing import Literal

from fastapi import FastAPI
from logtide_sdk import ClientOptions, LogTideClient
from logtide_sdk.middleware import LogTideFastAPIMiddleware

from src.config import settings

logtide_client = LogTideClient(
    ClientOptions(
        api_url="https://api.logtide.dev",
        api_key=settings.LOGTIDE_TOKEN or "",
        auto_trace_id=False,
        global_metadata={"env": settings.ENV},
    )
)


def add_logtide_middleware(app: FastAPI) -> None:
    app.add_middleware(
        LogTideFastAPIMiddleware,
        client=logtide_client,
        service_name="server",  # maybe change to server-fastapi
    )


LogtideService = Literal["server", "worker"]
