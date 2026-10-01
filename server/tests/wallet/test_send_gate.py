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
