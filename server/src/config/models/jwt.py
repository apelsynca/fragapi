from pydantic import BaseModel, SecretStr


class JWT(BaseModel):
    secret_key: SecretStr
    algorithm: str = "HS256"
