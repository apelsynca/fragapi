# Telegram Log Module — Bug Fix Plan

Findings from review of `src/telegram_log/` and its bot handlers (`src/bot/logs/handlers.py`).
Bugs are ordered by severity. Each item lists root cause, affected locations, and the fix.

---

## Bug 1 (Primary): Editing chat_id reports success but does not edit

**Symptom:** set chat_id, then try to edit it → bot replies "changed" but the stored value is unchanged.

**Root cause:** `src/bot/logs/handlers.py:78-80` (`on_logs_target_changed`) performs the
"chat occupied?" lookup with `message.chat.id` (the chat the user is typing **in**) instead of
`message.text` (the new chat id the user **entered**).

When the user's existing source already points at the chat they are typing in (typical after
using "target this chat"), `get_source_by_chat_id()` finds it, `source.user == user`, and the
`set_source()` call — which only runs inside `except ResourceNotFound` — never executes.
Line 90 still unconditionally replies `CHANGED_TARGET_CHAT_ID`.

**Consequence of the same mistake:** if the user *types* a chat_id owned by another user,
it is never detected → `set_source()` INSERTs a duplicate `chat_id` → `IntegrityError`
(unique constraint, `src/models/telegram_logs_sources.py:15`) instead of the intended
`THIS_CHAT_ID_ALREADY_OCCUPIED` reply.

**Fix** (`src/bot/logs/handlers.py`, `on_logs_target_changed`):
1. Run the occupancy check against the **entered text**:
   `get_source_by_chat_id(session=session, chat_id=message.text)`.
2. If found and owned by another user → reply `THIS_CHAT_ID_ALREADY_OCCUPIED` and
   `state.clear()` before returning (see Bug 4).
3. Otherwise call `set_source(session, user, chat_id=message.text)` **unconditionally** —
   including when a source already exists for this user (that is the "edit" path).
4. Only then send the success message and refreshed menu.

---

## Bug 2: `target_this_chat` can delete another user's source

`src/bot/logs/handlers.py:108-114` (`set_logs_target_as_this_chat`) deletes the found source
without checking ownership (unlike line 81). In a shared chat (e.g. a group where the bot
posted the keyboard), user B can silently delete user A's source and claim the chat_id.

**Fix:** after `get_source_by_chat_id(...)`, if `source.user != user` → treat as occupied
(alert text) and return without deleting. Only delete when the source belongs to the caller.
Note the explicit `delete()` is redundant anyway — `set_source()` already deletes the user's
sources — so after the ownership check the handler can just call `set_source()`.

---

## Bug 3: Wrong exception caught — `TelegramLogChatNotFound` is dead code

`src/telegram_log/sender.py:45` catches `TelegramNotFound` (HTTP 404), which the Bot API
effectively never returns for `send_message`. Real failures are:
- invalid/unknown chat_id → HTTP 400 `TelegramBadRequest` ("chat not found")
- user blocked the bot → HTTP 403 `TelegramForbiddenError`

Because neither is caught, `TelegramLogChatNotFound` never propagates, the graceful handler
at `src/telegram_log/tasks.py:20-21` never runs, and real failures fall into the generic
`except Exception` → logged + re-raised → task fails/retries endlessly.

**Fix** (`src/telegram_log/sender.py`):
```python
except (TelegramBadRequest, TelegramForbiddenError) as e:
    if isinstance(e, TelegramBadRequest) and "chat not found" not in str(e):
        raise
    raise TelegramLogChatNotFound() from e
```
Import both from `aiogram.exceptions`.

---

## Bug 4: FSM state not cleared on "occupied" error

`src/bot/logs/handlers.py:82-83` — early `return` on `THIS_CHAT_ID_ALREADY_OCCUPIED`
without `state.clear()`: the user stays stuck in `TelegramLogsForm.target` and every
subsequent message re-enters the handler.

**Fix:** call `await state.clear()` before the `return` (or clear at the top of the failure
branch). Same applies to any other early-return failure paths added in Bug 1's fix.

---

## Bug 5: No chat_id validation

`src/telegram_log/service.py:11-13` — `validate_chat_id_or_smth` only does `str(...)`;
free text like `"abc"` is stored, then fails at send time (compounded by Bug 3).

**Fix:** in `validate_chat_id_or_smth`, require a string of digits (optionally leading `-`
for group chats), e.g. `if not re.fullmatch(r"-?\d+", str(chat_id)): raise BadRequest(...)`
(or return a sentinel the handler maps to a user-facing error). Keep the normalization
`str(chat_id)` for the numeric input from `target_this_chat`.

---

## Bug 6: `ton_transaction` accessed without a `None` guard

`src/telegram_log/transaction.py:72-74` — `to_amount(transaction.ton_transaction.nano_amount)`
has no guard, while lines 76-82 clearly anticipate a missing `ton_transaction`
(`if transaction.ton_transaction.hash ... else "transaction"`). A transaction without one →
`AttributeError` (line 78 checks `.hash`, not `ton_transaction` itself).

**Fix:** early in `enqueue_transaction_admin_log_task`, branch on
`transaction.ton_transaction is None`:
- if present: compute `fee_amount` and `head_title_url` with the tx hash link
- if absent: `fee_amount = 0` and `head_title_url = "transaction"`
Replace the truthiness check on `.hash` with the guard on `ton_transaction`.

---

## Bug 7: `@None` rendered in messages

`src/telegram_log/transaction.py:42` and `:90` — `@{username}` renders `@None` when
`recipient_username` is `None`.

**Fix:** `username=f"@{transaction.recipient_username}" if transaction.recipient_username
else "<i>unknown</i>"` (or a localized/English equivalent per text language) in both
user and admin templates.

---

## Minor items (optional, cheap)

| Location | Issue | Fix |
|---|---|---|
| `service.py:39` | Typo `"Aready have a source"` | `"Already have a source"` |
| `tasks.py:13` | `chat_id: int` annotation but callers pass `str` (`source.chat_id` is `Mapped[str]`, `transaction.py:37`) | annotate `chat_id: str` (or `int \| str` + document) |
| `handlers.py:112` | Redundant delete before `set_source` (which deletes user's sources itself) | drop once Bug 2's ownership check is in |
| `service.py` `set_source` | delete-then-insert can hit unique(chat_id) under concurrent race for the same chat_id | acceptable; optionally catch `IntegrityError` → `BadRequest("chat_id is busy")` |

---

## Verification plan

1. **Unit tests** (`tests/telegram_log/test_service.py`) — extend:
   - `set_source` when a **different user** already owns the entered chat_id → expect
     `IntegrityError` (documents today's behavior) and, after adding the optional
     `IntegrityError` handling, `BadRequest`.
   - `validate_chat_id_or_smth` accepts `123`, `-100200300`, `12345` (int and str) and
     rejects `"abc"`, `"12 34"`, `""`.
2. **Bot flow tests** (add `tests/bot/logs/…` with mocked FSM + session, if handler tests
   exist — otherwise manual):
   - set target to current chat → edit to a **new** id via typed text → DB row must show the
     new id and menu must display it (regression test for Bug 1).
   - typed chat_id owned by another user → `THIS_CHAT_ID_ALREADY_OCCUPIED` reply, state
     cleared, no DB change.
   - `target_this_chat` in a chat owned by another user → alert, other user's row untouched.
3. **Sender tests** (`tests/telegram_log/test_tasks.py`):
   - `TelegramBadRequest("...chat not found...")` and `TelegramForbiddenError` from the
     sender → task logs `chat_not_found`, does not re-raise.
   - `TelegramBadRequest` with a different message → re-raised.
4. **Regression sweep:** `pytest tests/telegram_log tests/transaction tests/deposit -q`,
   then full suite; run the project's lint/typecheck (e.g. `ruff` / `mypy` per repo config).

## Suggested implementation order

1. Bug 1 + Bug 4 (same handler, one edit)
2. Bug 2 (same file)
3. Bug 3 (`sender.py`) + Bug 5 (`service.py` validation)
4. Bug 6 + Bug 7 (`transaction.py`)
5. Minor items + tests
