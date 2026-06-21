from typing import Literal

from fastapi import FastAPI
from logtide_sdk import ClientOptions, LogTideClient
from logtide_sdk.middleware import LogTideFastAPIMiddleware

from src.config import settings


class FakeLogtideClient(LogTideClient):
    def __init__(self) -> None:
        self._trace_id = None

    def log(self, entry) -> None:
        pass


def get_logtide_client() -> LogTideClient:
    if not settings.LOGTIDE_TOKEN:
        return FakeLogtideClient()

    return LogTideClient(
        ClientOptions(
            api_url="https://api.logtide.dev",
            api_key=settings.LOGTIDE_TOKEN,
            auto_trace_id=False,
            global_metadata={"env": settings.ENV},
        )
    )


logtide_client = get_logtide_client()


def add_logtide_middleware(app: FastAPI, client: LogTideClient) -> None:
    app.add_middleware(LogTideFastAPIMiddleware, client=client, service_name="server")


LogtideService = Literal["server", "worker"]
