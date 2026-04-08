import logging.config
import uuid
from typing import Any, TypeVar

import structlog

from src.config import settings

RendererType = TypeVar("RendererType")

Logger = structlog.stdlib.BoundLogger


class Logging[RendererType]:
    """Hubben logging configurator of `structlog` and `logging`.

    Customized implementation inspired by the following documentation:
    https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
    """

    timestamper = structlog.processors.TimeStamper(fmt="%H:%M:%S", utc=False)

    @classmethod
    def get_level(cls) -> str:
        return settings.log_level

    @classmethod
    def get_processors(cls) -> list[Any]:
        return [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            cls.timestamper,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]

    @classmethod
    def get_renderer(cls) -> RendererType:
        raise NotImplementedError()

    @classmethod
    def configure_stdlib(cls) -> None:
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
                        for logger in ["uvicorn", "sqlalchemy"]
                    },
                    **{
                        logger: {
                            "handlers": [],
                            "level": "INFO"
                            if level == "DEBUG"
                            else level,  # disable debug logs
                            "propagate": True,
                        }
                        for logger in ["telegram", "httpcore"]
                    },
                },
            }
        )

    @classmethod
    def configure_structlog(cls) -> None:
        structlog.configure_once(
            processors=cls.get_processors(),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    @classmethod
    def configure(cls) -> None:
        cls.configure_stdlib()
        cls.configure_structlog()


# before there was DevRenderer and ProdRenderer...
class DefaultRenderer(Logging[structlog.dev.ConsoleRenderer]):
    @classmethod
    def get_renderer(cls) -> structlog.dev.ConsoleRenderer:
        return structlog.dev.ConsoleRenderer(colors=True)


def configure() -> None:
    if settings.is_development():
        DefaultRenderer.configure()
    else:
        DefaultRenderer.configure()


def get_logger() -> Logger:
    return structlog.get_logger()


def generate_correlation_id() -> str:
    return str(uuid.uuid4())
