from fastapi import FastAPI
from logtide_sdk import ClientOptions, LogTideClient
from logtide_sdk.middleware import LogTideFastAPIMiddleware

from src.config import settings


def get_logtide_client() -> LogTideClient:
    return LogTideClient(
        ClientOptions(
            api_url="https://api.logtide.dev",
            api_key=settings.LOGTIDE_TOKEN,
            local_mode="if_unset_api_key",
            auto_trace_id=False,
            global_metadata={"env": settings.ENV},
        )
    )


logtide_client = get_logtide_client()


def add_logtide_middleware(app: FastAPI, client: LogTideClient) -> None:
    app.add_middleware(LogTideFastAPIMiddleware, client=client, service_name="server")
