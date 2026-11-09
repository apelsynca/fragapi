from collections.abc import AsyncGenerator

from src.redis import Redis, create_redis


async def get_worker_redis() -> AsyncGenerator[Redis]:
    async with create_redis("worker") as redis:
        yield redis
