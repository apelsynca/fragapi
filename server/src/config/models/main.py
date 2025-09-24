from datetime import timedelta

from pydantic import SecretStr
from pydantic_settings import BaseSettings

from .bot import Bot
from .environment import Environment
from .jwt import JWT
from .server import Server


class Settings(BaseSettings):
    database_url: SecretStr
    ton_api_key: SecretStr
    wallet_mnemonic: list[SecretStr]
    server: Server = Server()

    bot: Bot
    jwt: JWT
    user_session_ttl: timedelta = timedelta(days=7)
    log_level: str = "DEBUG"
    fragment_session_path: str = ".fragment-session.json"
    price_markup: float = 0.005  # 0.5%
    pagination_max_limit: int = 100

    docs_url: str = "https://docs.fragapi.ru"
    panel_url: str = "https://panel.fragapi.ru"
    env: Environment = Environment.development

    def get_secret_wallet_mnemonic(self) -> list[str]:
        return [word.get_secret_value() for word in self.wallet_mnemonic]

    def is_development(self) -> bool:
        return self.is_environment(Environment.development)

    def is_environment(self, environment: Environment) -> bool:
        return self.env == environment
