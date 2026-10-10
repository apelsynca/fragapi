import asyncio
from itertools import pairwise

import pytest
from fakeredis import FakeServer
from fakeredis.aioredis import FakeRedis

from src.wallet.send_gate import WalletSendGate


@pytest.mark.asyncio
async def test_100_jobs_across_two_workers_are_serialized():
    server = FakeServer()
    clients = [FakeRedis(server=server), FakeRedis(server=server)]
    gates = [WalletSendGate(c, "wallet", interval=0.01) for c in clients]
    active = 0
    peak = 0
    times = []
    loop = asyncio.get_running_loop()

    async def send(index):
        nonlocal active, peak
        async with gates[index % 2].attempt():
            active += 1
            peak = max(peak, active)
            times.append(loop.time())
            await asyncio.sleep(0.001)
            active -= 1

    await asyncio.wait_for(asyncio.gather(*(send(i) for i in range(100))), 20)
    assert peak == 1
    assert len(times) == 100
    assert all(b - a >= 0.009 for a, b in pairwise(times))
    for client in clients:
        await client.aclose()


@pytest.mark.asyncio
async def test_failure_consumes_cooldown():
    async with FakeRedis() as redis:
        gate = WalletSendGate(redis, "wallet", interval=0.05)
        loop = asyncio.get_running_loop()
        with pytest.raises(ValueError, match="failed"):
            async with gate.attempt():
                raise ValueError("failed")
        ended = loop.time()
        async with gate.attempt():
            assert loop.time() - ended >= 0.049


@pytest.mark.asyncio
async def test_crashed_owner_reserves_cooldown_after_lease_expiry():
    async with FakeRedis() as redis:
        gate = WalletSendGate(
            redis, "wallet", interval=0.02, attempt_timeout=0.02, lease=0.04
        )
        await redis.eval(
            gate._ACQUIRE, 2, gate.lock_key, gate.next_key, "crashed", 40, 20
        )
        started = asyncio.get_running_loop().time()
        async with gate.attempt():
            assert asyncio.get_running_loop().time() - started >= 0.059


@pytest.mark.asyncio
async def test_timed_out_attempt_releases_lock_and_consumes_cooldown():
    async with FakeRedis() as redis:
        gate = WalletSendGate(
            redis, "wallet", interval=0.02, attempt_timeout=0.01, lease=1
        )
        with pytest.raises(TimeoutError):
            async with gate.attempt():
                await asyncio.sleep(1)
        assert not await redis.exists(gate.lock_key)
        ended = asyncio.get_running_loop().time()
        async with gate.attempt():
            assert asyncio.get_running_loop().time() - ended >= 0.019


@pytest.mark.asyncio
async def test_pending_seqno_blocks_new_payment_until_chain_advances():
    async with FakeRedis(decode_responses=True) as redis:
        gate = WalletSendGate(redis, "wallet", interval=0)
        async with gate.attempt():
            await gate.reserve_seqno(12)
        async with gate.attempt():
            with pytest.raises(RuntimeError, match="unresolved"):
                await gate.reserve_seqno(12)
            await gate.reserve_seqno(13)
        assert await redis.get(gate.pending_key) == "13"


@pytest.mark.asyncio
async def test_stale_owner_cannot_reserve_or_broadcast_after_lease_loss():
    async with FakeRedis(decode_responses=True) as redis:
        gate = WalletSendGate(redis, "wallet", interval=0)
        with pytest.raises(RuntimeError, match="lease lost"):
            async with gate.attempt():
                await redis.set(gate.lock_key, "replacement-owner")
                with pytest.raises(RuntimeError, match="lease lost"):
                    await gate.reserve_seqno(1)
                with pytest.raises(RuntimeError, match="lease lost"):
                    await gate.assert_owned()
        assert await redis.get(gate.lock_key) == "replacement-owner"


@pytest.mark.asyncio
async def test_reservation_survives_response_loss():
    """Redis applies reservation but connection drops before Python receives response."""
    async with FakeRedis(decode_responses=True) as redis:
        gate = WalletSendGate(redis, "wallet", interval=0)

        async with gate.attempt():
            # Simulate connection drop after Redis applies the reservation
            original_eval = redis.eval
            call_count = 0

            async def failing_eval(script, num_keys, *args, **kwargs):
                nonlocal call_count
                result = await original_eval(script, num_keys, *args, **kwargs)
                # Fail only on the reserve_seqno call (which uses pending_key)
                if call_count == 0 and num_keys == 3 and "pending" in str(args):
                    call_count += 1
                    raise ConnectionError("response lost")
                return result

            # Temporarily patch eval to simulate connection drop
            redis.eval = failing_eval

            # First attempt: connection drops after Redis applies
            with pytest.raises(ConnectionError, match="response lost"):
                await gate.reserve_seqno(5)

            # Restore original eval
            redis.eval = original_eval

            # Despite exception, reservation was applied
            assert await redis.get(gate.pending_key) == "5"
            assert await redis.get(gate.pending_owner_key) == gate._token

            # Retry should recognize "already reserved by me" and succeed (idempotent)
            await gate.reserve_seqno(5)

            # Can still proceed with broadcast
            await gate.assert_owned()


@pytest.mark.asyncio
async def test_cleanup_releases_reservation_on_pre_broadcast_failure():
    """If reservation succeeds but broadcast fails, cleanup should release the seqno."""
    async with FakeRedis(decode_responses=True) as redis:
        gate = WalletSendGate(redis, "wallet", interval=0)

        async with gate.attempt():
            await gate.reserve_seqno(7)
            assert await redis.get(gate.pending_key) == "7"

            # Simulate cleanup after failure before broadcast
            released = await gate.release_seqno_if_owned(7)
            assert released is True

            # Reservation should be cleared
            assert await redis.get(gate.pending_key) is None
            assert await redis.get(gate.pending_owner_key) is None

        # Next attempt can reserve the same seqno
        async with gate.attempt():
            await gate.reserve_seqno(7)
            assert await redis.get(gate.pending_key) == "7"
