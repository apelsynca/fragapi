from src.redis import Redis
from src.schemas import BaseRecipient


class RecipientCache:
    async def get(self, redis: Redis, username: str) -> None | BaseRecipient:
        pass


recipient_cache = RecipientCache()
