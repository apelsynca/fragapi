import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logtide_sdk import LogTideClient
    from structlog.typing import EventDict, WrappedLogger

from logtide_sdk import LogEntry, LogLevel, serialize_exception

LOGGING_RESERVED_ATTRS: frozenset[str] = frozenset(
    [
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",  # 3.12+
    ]
)

FASTAPI_RELATED = {"websocket"}
RESERVED_ATTRS = (
    LOGGING_RESERVED_ATTRS | {"level", "event", "timestamp"} | FASTAPI_RELATED
)


class LogTideProcessor:
    def __init__(self, client: "LogTideClient", service: str) -> None:
        self.client = client
        self.service = service

    def __call__(
        self, logger: "WrappedLogger", name: str, event_dict: "EventDict"
    ) -> "EventDict":
        metadata = {k: v for k, v in event_dict.items() if k not in RESERVED_ATTRS}

        for m_key, value in metadata.items():
            if not isinstance(value, (str, int, float, bool, type(None))):
                metadata[m_key] = repr(value)

        exc_info = event_dict.get("exc_info", False)
        if exc_info:
            if exc_info is True:
                exc_info = sys.exc_info()
            if isinstance(exc_info, tuple):
                exc_info = exc_info[1]
            if isinstance(exc_info, BaseException):
                metadata["exception"] = serialize_exception(exc_info)
            elif exc_info is not None:
                raise TypeError(
                    f"Invalid type for exc_info: {exc_info.__class__.__name__}"
                )

        level = self._map_level(event_dict.get("level", "info"))
        msg = event_dict.get("event") or "structlog event"

        self.client.log(
            entry=LogEntry(
                service=self.service,
                level=level,
                message=msg,
                metadata=metadata,
            )
        )

        return event_dict

    def _map_level(self, raw_level: str) -> LogLevel:
        raw_level = raw_level.lower()
        if raw_level == "warning":
            raw_level = "warn"
        return LogLevel(raw_level)
