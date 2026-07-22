from datetime import timedelta
from typing import Literal

import structlog

from src.logging import Logger
from src.redis import Redis
from src.schemas import BaseRecipient

RecipientServiceName = Literal["stars", "prem"]

log: Logger = structlog.get_logger()


class RecipientCache:
    def __init__(self, service: RecipientServiceName) -> None:
        self.caching_key = f"rec:{service}"
        self.expiration_time = timedelta(minutes=10)

    async def get(self, redis: Redis, username: str) -> None | BaseRecipient:
        redis_data = await redis.get(name=self._get_name(username))

        if redis_data is None:
            return None

        try:
            return BaseRecipient.model_validate_json(redis_data)
        except Exception:
            log.error("Error getting by recipient cache")

    async def set(self, redis: Redis, recipient: BaseRecipient, username: str) -> None:
        json_dump = BaseRecipient(**recipient.model_dump()).model_dump_json(
            exclude_unset=True
        )
        await redis.set(
            name=self._get_name(username),
            value=json_dump,
            ex=self.expiration_time,
        )

    def _get_name(self, username: str) -> str:
        return f"{self.caching_key}:{username}"


stars_recipient_cache = RecipientCache(service="stars")
premium_recipient_cache = RecipientCache(service="prem")
