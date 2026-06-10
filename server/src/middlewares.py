import contextlib

import structlog
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.logging import TraceID
from src.logtide import logtide_client
from src.worker import TaskQueueManager


class LogTraceIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        trace_id = TraceID.set()

        structlog.contextvars.bind_contextvars(
            trace_id=trace_id,
            method=scope["method"],
            path=scope["path"],
        )

        logtide_stack = contextlib.ExitStack()
        logtide_stack.enter_context(logtide_client.with_trace_id(trace_id=trace_id))

        try:
            await self.app(scope, receive, send)
        finally:
            logtide_stack.close()
            structlog.contextvars.unbind_contextvars("trace_id", "method", "path")
            TraceID.clear()


class KiqEnqueuedTasksMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        async with TaskQueueManager.open():
            await self.app(scope, receive, send)


class SandboxResponseHeaderMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                headers = MutableHeaders(scope=message)
                headers["X-Frag-Sandbox"] = "1"
            await send(message)

        await self.app(scope, receive, send_wrapper)
