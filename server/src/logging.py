import logging.config
import uuid
from typing import Any

import structlog

from src.config import settings
from src.logtide import LogtideService, logtide_client
from src.logtide_structlog import LogTideProcessor

Logger = structlog.stdlib.BoundLogger


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
                            *(
                                [
                                    LogTideProcessor(
                                        client=logtide_client, service=logtide_service
                                    )
                                ]
                                if logtide_service
                                else []
                            ),
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


def generate_correlation_id() -> str:
    return str(uuid.uuid4())
