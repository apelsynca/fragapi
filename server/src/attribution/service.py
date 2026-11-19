import asyncio
import re
import secrets

import structlog
from pydantic import ValidationError

from redis import RedisError
from src.attribution.schemas import Attribution
from src.config import settings
from src.redis import Redis

log = structlog.get_logger()

TOKEN_TTL_SECONDS = 30 * 24 * 60 * 60
TOKEN_PREFIX = "signup-attribution:"
LOGIN_PREFIX = "login_a_"
SOURCE_PREFIX = "src_"
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_-]{24}")


async def create_start_argument(redis: Redis, attribution: Attribution) -> str:
    if attribution.is_empty:
        return "login"
    token = secrets.token_urlsafe(18)
    try:
        async with asyncio.timeout(1):
            await redis.set(
                TOKEN_PREFIX + token,
                attribution.model_dump_json(),
                ex=TOKEN_TTL_SECONDS,
            )
    except (RedisError, TimeoutError):
        log.warning("Signup attribution storage unavailable")
        return "login"
    return LOGIN_PREFIX + token


async def resolve_start_argument(
    argument: str | None, redis: Redis | None
) -> Attribution | None:
    if not argument or len(argument) > 64:
        return None
    try:
        if argument.startswith(SOURCE_PREFIX):
            campaign = settings.SIGNUP_CAMPAIGNS.get(argument[len(SOURCE_PREFIX) :])
            return Attribution.model_validate(campaign) if campaign else None
        if argument.startswith(LOGIN_PREFIX) and redis is not None:
            token = argument[len(LOGIN_PREFIX) :]
            if not TOKEN_PATTERN.fullmatch(token):
                return None
            async with asyncio.timeout(1):
                value = await redis.get(TOKEN_PREFIX + token)
            if value:
                return Attribution.model_validate_json(value)
    except (RedisError, TimeoutError, ValidationError):
        log.warning("Signup attribution unavailable or invalid")
    return None
