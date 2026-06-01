import os
from datetime import timedelta
from enum import StrEnum
from typing import Literal

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.enums import TelegramLogSender


class Environment(StrEnum):
    development = "development"
    testing = "testing"  # Used for running tests
    production = "production"


env = Environment(os.getenv("FRAG_ENV", Environment.development))
if env == Environment.testing:
    env_file = ".env.testing"
else:
    env_file = ".env"


class Settings(BaseSettings):
    ENV: Environment = Environment.development
    LOG_LEVEL: str = "DEBUG"

    TON_ADDRESS: str = ""
    TONCENTER_API_KEY: str = ""
    TONAPI_API_KEY: str = ""
    WALLET_MNEMONIC: list[str] = []

    # User session
    USER_SESSION_TTL: timedelta = timedelta(days=7)

    # Database
    POSTGRES_USER: str = "frag"
    POSTGRES_PWD: str = "frag"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE: str = "frag_dev"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_POOL_RECYCLE_SECONDS: int = 600  # 10 minutes
    DATABASE_COMMAND_TIMEOUT_SECONDS: float = 30.0

    # Bot
    BOT_TOKEN: str = ""
    BOT_WEBHOOK_URL: str = ""
    BOT_WEBHOOK_PATH: str = "/bot/webhook"
    BOT_WEBHOOK_SECRET_TOKEN: str | None = None

    # LogTide
    LOGTIDE_TOKEN: str | None = None

    # Application behaviours
    API_PRICE_MARKUP: float = Field(gt=0, default=0.01)
    API_PAGINATION_MAX_LIMIT: int = 100
    MIN_TON_DEPOSIT_AMOUNT: float = Field(gt=0, default=0.25)
    MIN_NON_SILENT_AMOUNT: float = 3

    TELEGRAM_LOG_SENDER: TelegramLogSender = TelegramLogSender.logger
    TELEGRAM_LOGS_CHAT_ID: int | str = ""

    DOCS_URL: str = "https://docs.fragapi.com"
    API_URL: str = "https://api.fragapi.com"
    PANEL_URL: str = "https://fragapi.com"

    FRAGMENT_SESSION_PATH: str = ""

    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    AMQP_HOST: str = "127.0.0.1"
    AMQP_USER: str = "guest"
    AMQP_PWD: str = "guest"
    AMQP_PORT: int = 5672

    @property
    def amqp_url(self) -> str:
        return f"amqp://{self.AMQP_USER}:{self.AMQP_PWD}@{self.AMQP_HOST}:{self.AMQP_PORT}/"

    def get_postgres_dsn(self, driver: Literal["asyncpg", "psycopg2"]) -> str:
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{driver}",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PWD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DATABASE,
            )
        )

    def is_production(self) -> bool:
        return self.is_environment({Environment.production})

    def is_development(self) -> bool:
        return self.is_environment({Environment.development})

    def is_testing(self) -> bool:
        return self.is_environment({Environment.testing})

    def is_environment(self, environments: set[Environment]) -> bool:
        return self.ENV in environments

    model_config = SettingsConfigDict(
        env_prefix="frag_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_file=env_file,
    )


settings = Settings()
