import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4

from redis.asyncio import Redis
from redis.asyncio.retry import Retry
from redis.backoff import NoBackoff

from src.config import settings


class WalletSendGate:
    """Shared, fail-closed wallet serialization with a post-attempt cooldown."""

    # A crashed owner reserves a full lease plus the cooldown. Normal completion
    # atomically replaces that reservation with a cooldown measured by Redis.
    _ACQUIRE = """
    local t = redis.call('TIME')
    local now = t[1] * 1000 + math.floor(t[2] / 1000)
    local next = tonumber(redis.call('GET', KEYS[2]) or '0')
    if redis.call('EXISTS', KEYS[1]) == 1 then return 100 end
    if next > now then return math.min(next - now, 100) end
    redis.call('SET', KEYS[1], ARGV[1], 'PX', ARGV[2])
    redis.call('SET', KEYS[2], now + ARGV[2] + ARGV[3])
    return 0
    """
    _RELEASE = """
    if redis.call('GET', KEYS[1]) ~= ARGV[1] then return 0 end
    local t = redis.call('TIME')
    local now = t[1] * 1000 + math.floor(t[2] / 1000)
    redis.call('SET', KEYS[2], now + ARGV[2])
    redis.call('DEL', KEYS[1])
    return 1
    """

    def __init__(
        self,
        redis: Redis,
        wallet_id: str,
        *,
        interval: float = 3,
        attempt_timeout: float = 30,
        lease: float = 60,
    ) -> None:
        if interval < 0 or attempt_timeout <= 0 or lease <= attempt_timeout:
            raise ValueError("Lease must exceed the positive attempt timeout")
        self.redis = redis
        self.lock_key = f"wallet:{{{wallet_id}}}:send-lock"
        self.next_key = f"wallet:{{{wallet_id}}}:next-send-at"
        self.pending_key = f"wallet:{{{wallet_id}}}:pending-seqno"
        self._token: str | None = None
        self.interval = interval
        self.attempt_timeout = attempt_timeout
        self.lease = lease

    @asynccontextmanager
    async def attempt(self):
        token = uuid4().hex
        while True:
            delay_ms = await self.redis.eval(
                self._ACQUIRE,
                2,
                self.lock_key,
                self.next_key,
                token,
                int(self.lease * 1000),
                int(self.interval * 1000),
            )
            if delay_ms == 0:
                break
            await asyncio.sleep(delay_ms / 1000)

        try:
            self._token = token
            async with asyncio.timeout(self.attempt_timeout):
                yield
        finally:
            self._token = None
            # On Redis failure leave the lease/reservation intact, failing closed.
            released = await self.redis.eval(
                self._RELEASE,
                2,
                self.lock_key,
                self.next_key,
                token,
                int(self.interval * 1000),
            )
            if not released:
                raise RuntimeError("Wallet send lease lost")

    async def reserve_seqno(self, seqno: int) -> None:
        """Atomically fence signing against stale owners and unresolved sends.

        The reservation intentionally has no TTL. A timeout is not evidence that
        the prior payment failed; unresolved seqnos require chain/manual recovery.
        """
        result = await self.redis.eval(
            """
            if redis.call('GET', KEYS[1]) ~= ARGV[1] then return -1 end
            local pending = redis.call('GET', KEYS[2])
            if pending and tonumber(pending) >= tonumber(ARGV[2]) then return 0 end
            redis.call('SET', KEYS[2], ARGV[2])
            return 1
            """,
            2,
            self.lock_key,
            self.pending_key,
            self._token or "",
            seqno,
        )
        if result == -1:
            raise RuntimeError("Wallet send lease lost before signing")
        if result == 0:
            raise RuntimeError("Previous wallet seqno is unresolved; defer signing")

    async def assert_owned(self) -> None:
        if not self._token or await self.redis.get(self.lock_key) != self._token:
            raise RuntimeError("Wallet send lease lost before broadcast")


def create_wallet_send_redis() -> Redis:
    # Coordination must fail promptly, rather than silently retrying for minutes
    # while an owner's lease expires.
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_timeout=2,
        socket_connect_timeout=2,
        retry=Retry(NoBackoff(), retries=0),
        client_name=f"{settings.ENV.value}.wallet-send",
    )
