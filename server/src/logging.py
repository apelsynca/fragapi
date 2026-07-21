import contextvars
import logging.config
import typing
import uuid
from typing import Any, Literal

import structlog
from logtide_sdk.structlog import LogTideProcessor

from src.config import settings
from src.logtide import logtide_client

Logger = structlog.stdlib.BoundLogger

LogtideService = Literal["server", "worker"]


class Logging[RendererType]:
    """Hubben logging configurator of `structlog` and `logging`.

    Customized implementation inspired by the following documentation:
    https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
    """

    timestamper = structlog.processors.TimeStamper(fmt="%H:%M:%S", utc=False)

    @classmethod
    def get_level(cls) -> str:
        return settings.LOG_LEVEL

    @classmethod
    def get_processors(
        cls, *, logtide_service: LogtideService | None = None
    ) -> list[Any]:
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            cls.timestamper,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            *(
                [LogTideProcessor(client=logtide_client, service=logtide_service)]
                if logtide_service
                else []
            ),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]

        return processors

    @classmethod
    def get_renderer(cls) -> RendererType:
        raise NotImplementedError()

    @classmethod
    def configure_stdlib(cls, *, logtide_service: LogtideService | None = None) -> None:
        level = cls.get_level()

        optional_logtide_proc = (
            [LogTideProcessor(client=logtide_client, service=logtide_service)]
            if logtide_service
            else []
        )

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": {
                    "fragapi": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            cls.get_renderer(),
                        ],
                        "foreign_pre_chain": [
                            structlog.contextvars.merge_contextvars,
                            structlog.stdlib.add_log_level,
                            structlog.stdlib.add_logger_name,
                            structlog.stdlib.PositionalArgumentsFormatter(),
                            structlog.stdlib.ExtraAdder(),
                            cls.timestamper,
                            structlog.processors.UnicodeDecoder(),
                            structlog.processors.StackInfoRenderer(),
                            *optional_logtide_proc,
                            structlog.processors.format_exc_info,
                        ],
                    },
                },
                "handlers": {
                    "default": {
                        "level": level,
                        "class": "logging.StreamHandler",
                        "formatter": "fragapi",
                    },
                },
                "loggers": {
                    "": {
                        "handlers": ["default"],
                        "level": level,
                        "propagate": False,
                    },
                    # Propagate third-party loggers to the root one
                    **{
                        logger: {
                            "handlers": [],
                            "propagate": True,
                        }
                        for logger in ["sqlalchemy", "uvicorn", "logtide"]
                    },
                },
            }
        )

    @classmethod
    def configure_structlog(
        cls, *, logtide_service: LogtideService | None = None
    ) -> None:
        structlog.configure_once(
            processors=cls.get_processors(logtide_service=logtide_service),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    @classmethod
    def configure(cls, *, logtide_service: LogtideService | None) -> None:
        cls.configure_stdlib(logtide_service=logtide_service)
        cls.configure_structlog(logtide_service=logtide_service)


class Development(Logging[structlog.dev.ConsoleRenderer]):
    @classmethod
    def get_renderer(cls) -> structlog.dev.ConsoleRenderer:
        return structlog.dev.ConsoleRenderer(colors=True)


class Production(Logging[structlog.dev.ConsoleRenderer]):
    @classmethod
    def get_renderer(cls) -> structlog.dev.ConsoleRenderer:
        return structlog.dev.ConsoleRenderer(colors=True)


def configure(*, logtide_service: LogtideService | None = None) -> None:
    if settings.is_testing():
        Development.configure(logtide_service=None)
    if settings.is_development():
        Development.configure(logtide_service=logtide_service)
    else:
        Production.configure(logtide_service=logtide_service)


class TraceID:
    _trace_id: typing.ClassVar[contextvars.ContextVar[str | None]] = (
        contextvars.ContextVar("app.trace_id", default=None)
    )

    @classmethod
    def set(cls) -> str:
        correlation_id = str(uuid.uuid4())
        cls._trace_id.set(correlation_id)
        return correlation_id

    @classmethod
    def get(cls) -> str | None:
        return cls._trace_id.get()

    @classmethod
    def clear(cls) -> None:
        cls._trace_id.set(None)
