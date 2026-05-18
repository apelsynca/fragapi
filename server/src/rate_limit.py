from collections.abc import Sequence

from ratelimit import RateLimitMiddleware, Rule
from ratelimit.auths import EmptyInformation
from ratelimit.auths.ip import client_ip
from ratelimit.backends.redis import RedisBackend
from ratelimit.types import ASGIApp, Scope

from src.auth.models import AuthSubject, Subject, is_anonymous
from src.config import Environment, settings
from src.enums import RateLimitGroup
from src.redis import create_redis


async def _authenticate(scope: Scope) -> tuple[str, RateLimitGroup]:
    auth_subject: AuthSubject[Subject] = scope["state"]["auth_subject"]

    if is_anonymous(auth_subject):
        try:
            ip, _ = await client_ip(scope)
            return ip, RateLimitGroup.default
        except (EmptyInformation, ValueError, TypeError):
            return auth_subject.rate_limit_key

    return auth_subject.rate_limit_key


_BASE_RULES: dict[str, Sequence[Rule]] = {
    "^/v1/stars/buy": [Rule(minute=60, block_time=300, zone="buy")],
    "^/v1/premium/buy": [Rule(minute=60, block_time=300, zone="buy")],
    "^/v1/ton/rate": [Rule(minute=30)],
}

_PRODUCTION_RULES: dict[str, Sequence[Rule]] = {
    **_BASE_RULES,
    "^/v1": [
        Rule(group=RateLimitGroup.default, minute=500, zone="api"),
        Rule(group=RateLimitGroup.web, second=100, zone="api"),
    ],
}


def get_middleware(app: ASGIApp) -> RateLimitMiddleware:
    match settings.ENV:
        case Environment.production:
            rules = _PRODUCTION_RULES
        case _:
            rules = {}

    return RateLimitMiddleware(
        app, _authenticate, RedisBackend(create_redis("rate-limit")), rules
    )


__all__ = ["get_middleware"]
