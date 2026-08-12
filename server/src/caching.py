from datetime import timedelta
from typing import Literal

import structlog

from src.config import settings
from src.logging import Logger
from src.redis import Redis
from src.schemas import BaseRecipient

RecipientServiceName = Literal["stars", "prem"]

log: Logger = structlog.get_logger()


class RecipientCache:
    def __init__(
        self,
        service: RecipientServiceName,
        *,
        cache_time: timedelta = settings.RECIPIENT_CACHE_TIME,
    ) -> None:
        self.caching_key = f"rec:{service}"
        self.cache_time = cache_time

    async def get(self, redis: Redis, username: str) -> None | BaseRecipient:
        redis_data = await redis.get(name=self._get_name(username))

        if redis_data is None:
            return None

        log.debug("Pulled recipient data from cache", username=username)

        try:
            return BaseRecipient.model_validate_json(redis_data)
        except Exception:
            log.exception("Error getting by recipient cache")

    async def set(self, redis: Redis, recipient: BaseRecipient, username: str) -> None:
        json_dump = BaseRecipient(**recipient.model_dump()).model_dump_json(
            exclude_unset=True
        )
        try:
            await redis.set(
                name=self._get_name(username),
                value=json_dump,
                ex=self.cache_time,
            )
        except Exception:
            log.exception("Error setting the recipient cache")

    def _get_name(self, username: str) -> str:
        return f"{self.caching_key}:{username}"


stars_recipient_cache = RecipientCache(service="stars")
premium_recipient_cache = RecipientCache(service="prem")
