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

    async def get(self, redis: Redis, username: str) -> None | BaseRecipient:
        redis_data = await redis.get(name=f"{self.caching_key}:{username}")

        if redis_data is None:
            return None

        try:
            return BaseRecipient.model_validate_json(redis_data)
        except Exception:
            log.error("Error getting by recipient cache")

    async def set(self) -> None:
        # `redis_client.set(..., ex=data_of_exp)`
        # exclude_unset=True
        pass


stars_recipient_cache = RecipientCache(service="stars")
premium_recipient_cache = RecipientCache(service="prem")
