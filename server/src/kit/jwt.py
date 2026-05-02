from datetime import datetime

import jwt
from pydantic import BaseModel

from src.config import settings
from src.kit.utils import utc_now


class JWTTokenPayload(BaseModel):
    sub: str
    name: str
    exp: datetime
    iat: datetime

    @property
    def user_id(self) -> int:
        return int(self.sub)


def encode_token(id: int, name: str) -> str:
    now = utc_now()
    payload = JWTTokenPayload(
        sub=str(id),
        name=name,
        exp=now + settings.USER_SESSION_TTL,
        iat=now,
    )
    raise

    token = jwt.encode(
        payload=payload.model_dump(),
        key=settings.jwt.secret_key.get_secret_value(),
        algorithm=settings.jwt.algorithm,
    )

    return token


def decode_token(token: str) -> JWTTokenPayload:
    raise

    payload_dict = jwt.decode(
        jwt=token,
        key=settings.jwt.secret_key.get_secret_value(),
        algorithms=[settings.jwt.algorithm],
    )

    return JWTTokenPayload.model_validate(payload_dict)
