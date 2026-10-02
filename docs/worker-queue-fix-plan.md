# Simple wallet queue fix plan

## Goal

Keep the current architecture and make it reliable without adding a new model:

- `/buy` remains non-blocking.
- Wallet sends never overlap.
- Every attempt is followed by a three-second cooldown, including failures.
- A timeout cannot cause a duplicate payment.
- Other worker tasks remain concurrent.

## 1. Keep the existing data model

Do not add `WalletSendJob` or delivery-status fields to `Transaction`.

Keep only the existing transaction data plus `outgoing_message_hash`, which is
needed because it identifies the exact external message submitted to TON. Use
`TonTransaction.hash` for the blockchain transaction hash after reconciliation.

The existing task payload remains the source of the queued purchase. The current
RabbitMQ/Taskiq setup is sufficient for this scope.

## 2. Fix wallet serialization

Keep `WalletSendGate` as the only wallet-specific coordination mechanism:

1. Acquire the shared Redis lock.
2. Wait until the previous attempt's cooldown ends.
3. Refresh the wallet and build the message.
4. Persist `outgoing_message_hash` before broadcasting.
5. Broadcast exactly once.
6. Release the lock and start the three-second cooldown.

The Redis gate must remain independent of the general worker concurrency. Do not
set global `--max-async-tasks 1` or `--max-prefetch 1`.

## 3. Do not hold a database connection while waiting

The current task loads the transaction before entering the Redis gate. Refactor
the flow so the task does not keep a database transaction/session occupied while
waiting behind other wallet sends.

Use short database operations:

1. Load the transaction and validate its input.
2. Release/finish the database operation before waiting for the gate.
3. Acquire the Redis gate.
4. Reload the transaction and check `outgoing_message_hash`.
5. Save the outgoing hash in a short transaction before sending.
6. Save the resulting hash after sending.
7. Release the gate before notifications and hash lookup.

If the worker dependency provides one session for the whole task, explicitly use
a short-lived sessionmaker for these operations or restructure the dependency so
the session is not held during the Redis wait.

## 4. Handle errors correctly

Do not catch an exception, call `session.commit()`, and return success. A failed
database transaction must be rolled back before another database operation.

Use this simple policy:

- Validation/expired transaction: log and finish without broadcasting.
- Wallet/network failure before a message is persisted: let Taskiq retry the task.
- Failure after `outgoing_message_hash` is persisted: do not create a new message;
  reconcile the persisted external hash first.
- Successful broadcast: save the external hash and enqueue the existing lookup.

If Taskiq retries are enabled, configure bounded retries with backoff. Every retry
must pass through the Redis gate and consume the three-second cooldown.

## 5. Prevent duplicate sends

Before building a message, reload `outgoing_message_hash`:

- If it is present, do not call `wallet.transfer()` or broadcast another message.
- Enqueue/retry the existing blockchain lookup instead.
- If it is absent, build the message and persist its exact external hash before
  the first network submission.

For a timeout after submission may have occurred, search TON using that persisted
external hash. Do not blindly retry and do not refund based only on a timeout.

Give the existing lookup bounded retries/backoff and paginate through history to
cover the submission window. A missing lookup result is not proof of failure.

A hash alone cannot recover a crash between saving the hash and broadcasting.
Keep this limitation explicit: such a purchase needs reconciliation and follow-up,
not automatic replay. Safe automatic replay would require persisting the signed
message bytes, preferably on the existing `TonTransaction`; that is an optional
extension, not a new model.

## 6. Handle expired queued requests

100 requests require at least 297 seconds before all attempts can start. The
original `valid_until` may expire while waiting.

For the first implementation:

- Detect expiration before signing.
- Do not alter `valid_until` manually.
- Do not broadcast an expired message.
- Decide whether the product should refund expired, definitely-unsent purchases.

Payload regeneration can be added later if the Fragment flow supports recreating
the purchase safely. It is not required to implement the wallet serialization.

## 7. Validate TON seqno behavior separately

The three-second delay controls application pacing; it does not prove that TON
has accepted the previous wallet message. Record the unresolved seqno in Redis
while holding the wallet gate. Before signing the next payment, verify the wallet
has advanced past it. If it has not, defer signing and reconcile the preceding
message rather than build a different purchase with the same seqno.

Use bounded polling and explicit lease ownership checks. Confirmation may extend
the interval beyond three seconds. Validate this with the provider on testnet;
seqno advancement proves wallet acceptance, not successful purchase fulfillment.

## Implementation order

1. Refactor the task so database work is not held during Redis waiting.
2. Fix rollback/retry behavior; remove catch-and-return-success behavior.
3. Preserve and check `outgoing_message_hash` before every broadcast.
4. Keep the Redis gate scoped only to wallet sends and verify cooldown after errors.
5. Add expired-message handling and the refund decision.
6. Test with multiple workers, Redis, RabbitMQ, timeouts, crashes, and delayed TON
   seqno updates.

## Required tests

- 100 wallet tasks never overlap and respect the three-second cooldown.
- Unrelated worker tasks can execute concurrently.
- Database connections are not held while a wallet task waits.
- A failed pre-broadcast attempt is retried through Taskiq.
- A timeout after hash persistence never broadcasts a second message.
- An already-hashed transaction is skipped safely.
- An expired message is never broadcast.
- Test Redis lease loss and paused workers; cooperative timeouts alone do not
  guarantee an old sender has stopped. Do not claim multi-worker safety until
  these scenarios are resolved.
- A delayed TON seqno is handled safely in a testnet/provider integration test.

## Implemented behavior and remaining limits

- No new model or delivery-state fields were added.
- Wallet tasks commit short database operations before Redis waiting and provider
  calls, returning their pooled connections. Errors roll back and propagate.
- Opt-in Taskiq retry middleware makes up to five total attempts with increasing
  5/10/15/20-second delays through a RabbitMQ delay queue. Permanent validation
  errors do not retry. General worker concurrency remains unchanged.
- Redis atomically checks lease ownership and reserves a seqno before hash
  persistence. A subsequent purchase cannot reserve that seqno again. The current
  chain seqno must advance before signing another purchase.
- Reservations intentionally do not expire. If a reserved message never reaches
  TON (including a crash before hash persistence), the wallet pauses at that seqno
  for manual reconciliation. Do not clear the reservation unless the old sender
  and message can no longer execute. This favors preventing duplicate/conflicting
  sends over automatic recovery of an unknown outcome.
- Ownership is checked again before broadcast. Seqno reservation prevents two
  different purchases from using the same unresolved seqno, but a suspended old
  sender may still resume after its lease expires. Real multi-process pause/lease
  testing remains required before claiming absolute broadcast serialization.
- Lookup retries are bounded and paginate up to 100 pages of 100 transactions,
  stopping at the purchase creation window or a repeated cursor. Jobs beyond that
  history cap or still missing after retries require manual follow-up.
- Lookup tasks use their own Toncenter client; the sender's shared client lives
  for the worker lifecycle rather than being closed by concurrent tasks.
- Expired purchases are left for manual handling, with no automatic refund, per
  the user's decision. No manual extension of the payload deadline is performed.
- The crash between hash commit and broadcast remains a known manual-recovery
  case; signed-message storage/replay was not introduced.
- Full suite: 183 passing tests, including database-release, timeout deduplication,
  paginated lookup, seqno gating and stale-lease ownership checks. Real-service
  TON/RabbitMQ/Redis integration has not been performed in this session.
