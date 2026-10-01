# Serialized wallet worker queue

## Goal

`/buy` requests enqueue background jobs without waiting for wallet transfers.
The wallet processes one attempt at a time, waits three seconds after it finishes
(including a failure or timeout), then allows the next attempt. Exact FIFO ordering
is not required.

## Implementation

- Taskiq/RabbitMQ remains the background queue.
- The shared worker stays concurrent so wallet waits do not serialize unrelated tasks.
- `WalletSendGate` uses Redis keys scoped to the wallet address to coordinate sends
  across worker instances. Redis is available in every deployment.
- The gate uses a three-second cooldown, a 30-second attempt timeout, and a
  60-second lease. A crashed owner reserves the lease plus cooldown. Redis errors
  fail closed.
- Wallet refresh, message signing, and broadcasting happen inside the gate.
- The signed outgoing external-message hash is committed before broadcasting.
  A redelivery with that hash does not construct or submit another payment; it
  schedules a blockchain lookup instead.
- `sent_at` records successful submission or later discovery on-chain.
- Errors are logged. There is no persisted delivery state or attempt tracking.
- Migration `b82bdbf80731` adds only `outgoing_message_hash` and `sent_at`.
- Notifications and blockchain lookups happen outside the wallet gate.

## Submission versus confirmation

A successful send call means the provider accepted the submission, not that TON
included it on-chain. Queue pacing uses completion of the submission attempt.
The separate hash lookup searches the most recent 100 wallet transactions using
the persisted external-message hash, then stores the blockchain transaction hash
in `ton_transaction.hash`.

If the send times out after possibly reaching TON, the outgoing hash stays
persisted and prevents automatic rebroadcast. A missing blockchain lookup result
is not proof that the payment failed. There is no periodic state-based recovery
task; unresolved sends need follow-up reconciliation before any retry decision.

## Verification and rollout considerations

- Gate tests exercise 100 concurrent jobs across two independent Redis clients,
  cooldown after failure/timeout, and recovery after lease expiration.
- Transaction tests verify duplicate prevention, hash persistence after timeout,
  and rejection of expired queued messages.
- A real multi-process RabbitMQ/Redis deployment test remains a rollout check.
- A backlog of 100 takes at least 297 seconds plus send durations. Purchase
  payloads have a deadline and may expire while waiting. Regeneration/refunds
  require a separate business-policy decision.
- Three seconds alone does not guarantee the TON wallet seqno has advanced.
  Seqno coordination must be validated with the production provider.
- Reconciliation uses bounded history rather than paginated historical search.
- Validation errors before entering the gate retain the existing error behavior.
