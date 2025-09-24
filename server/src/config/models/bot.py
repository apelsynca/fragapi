from pydantic import BaseModel, SecretStr


class Bot(BaseModel):
    token: SecretStr
    webhook_url: str = "example.com"
    webhook_path: str = "/webhook/bot"
    webhook_secret_token: SecretStr | None = None
    should_set_commands: bool = False

    def get_webhook_secret_token(self) -> str | None:
        if self.webhook_secret_token:
            return self.webhook_secret_token.get_secret_value()
        return None
