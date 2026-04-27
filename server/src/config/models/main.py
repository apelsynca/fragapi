from datetime import timedelta
from typing import Literal

from pydantic import BaseModel, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings
from ton_core import NetworkGlobalID

from .bot import Bot
from .environment import Environment
from .jwt import JWT


class Database(BaseModel):
    user: str
    pwd: SecretStr
    host: str = "127.0.0.1"
    port: int = 5432
    name: str = "fragapi"


class Settings(BaseSettings):
    env: Environment = Environment.development

    database: Database
    ton_address: str
    toncenter_api_key: SecretStr
    wallet_mnemonic: list[SecretStr]

    bot: Bot
    jwt: JWT
    user_session_ttl: timedelta = timedelta(days=7)
    log_level: str = "DEBUG"
    fragment_session_path: str = ".fragment-session.json"
    price_markup: float = 0.005  # 0.5%
    pagination_max_limit: int = 100

    docs_url: str = "https://docs.fragapi.ru"
    panel_url: str = "https://panel.fragapi.ru"

    def get_secret_wallet_mnemonic(self) -> list[str]:
        return [word.get_secret_value() for word in self.wallet_mnemonic]

    def is_testing(self) -> bool:
        return self.is_environment(Environment.testing)

    def is_development(self) -> bool:
        return self.is_environment(Environment.development)

    def is_environment(self, environment: Environment) -> bool:
        return self.env == environment

    def get_env_network_id(self) -> NetworkGlobalID:
        return NetworkGlobalID.MAINNET

    def get_postgres_dsn(self, driver: Literal["asyncpg", "psycopg2"]) -> str:
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{driver}",
                username=self.database.user,
                password=self.database.pwd.get_secret_value(),
                host=self.database.host,
                port=self.database.port,
                path=self.database.name,
            )
        )
