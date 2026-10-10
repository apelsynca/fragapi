# Backend Refactoring and Fixes

## 1. REFACTORING OPPORTUNITIES

### A. Code Duplication & Pattern Inconsistencies

#### 1. Duplicate Sorting Pattern (HIGH PRIORITY)
**Location:** `src/transaction/service.py:70-71`, `src/deposit/service.py:33-34`

**Problem:** Both services duplicate the exact same pattern for handling default sorting.

```python
# transaction/service.py
if sorting is None:
    sorting = [(TransactionSortProperty.created_at, True)]

# deposit/service.py  
if sorting is None:
    sorting = [(DepositSortProperty.created_at, True)]
```

**Why problematic:** Violates DRY principle, makes future changes error-prone.

**Suggested fix:** Create a default sorting mechanism in the repository base class or use a decorator/mixin pattern.

---

#### 2. Inconsistent Error Handling in Fragment API (HIGH PRIORITY)
**Location:** `src/integrations/fragment/rest_client.py:81-95`

**Problem:** String-based error detection with lowercase comparison is fragile and hard to maintain.

```python
error_lowered = error_text.lower()
if "no telegram users found" in error_lowered:
    raise FragmentAPIUsersNotFound(error_text)
if "access denied" in error_lowered:
    raise FragmentAPIAccessDenied(error_text)
```

**Why problematic:** Fragile string matching, no error codes, difficult to test, prone to false positives.

**Suggested fix:** Use error codes if available, or create a mapping dictionary with compiled regex patterns.

---

#### 3. Hard-coded Magic Numbers (MEDIUM PRIORITY)
**Locations:**
- `src/fee.py:3` - `TON_FEE = 0.00582` (no comment explaining source)
- `src/integrations/fragment/main.py:12` - `CACHE_LT = 60 * 5  # 10 mins` (comment says 10, calculation is 5)
- `src/integrations/fragment/rest_client.py:22` - `STALE_TIME = 60 * 30`
- `src/wallet/send_gate.py:17-34` - Magic numbers in Lua scripts
- `src/transaction/service.py:157` - `days_count = 90`
- `src/transaction/tasks.py:132` - `valid_until = int(tc_transaction.valid_until.timestamp()) + 10`

**Why problematic:** No centralized configuration, unclear meaning, difficult to tune.

**Suggested fix:** Move to config.py as constants with documentation.

---

#### 4. Inconsistent Repository Pattern Usage (HIGH PRIORITY)
**Location:** `src/deposit/repository.py`, `src/transaction/repository.py`, `src/user/repository.py`

**Problem:** Each repository implements minimal methods, some have `get_by_id`, others don't, no consistent interface.

```python
# deposit/repository.py
class DepositRepository(BaseRepository[Deposit], SortingMixin):
    model = Deposit
    async def get_by_hash(self, hash: str) -> Deposit | None: ...
    
# transaction/repository.py  
class TransactionRepository(BaseRepository[Transaction], SortingMixin):
    model = Transaction
    async def get_by_id(self, id: UUID, options: Options | None = None) -> Transaction | None: ...
```

**Why problematic:** Inconsistent API surface, duplicated boilerplate, violates Liskov Substitution Principle.

**Suggested fix:** Define a protocol/interface with common methods (`get_by_id`, `get_by_*`, etc.) or use more complete base repository.

---

#### 5. Typo in Exception Class Name (EASY FIX - HIGH VISIBILITY)
**Location:** `src/exceptions.py:42`

**Problem:** `InsuficcientFunds` - misspelled "Insufficient"

```python
class InsuficcientFunds(BadRequest):  # Should be "Insufficient"
```

**Why problematic:** Unprofessional, breaks naming conventions, confusing for developers.

**Suggested fix:** Rename to `InsufficientFunds` (breaking change, needs migration).

---

#### 6. Complex Transaction Processing Logic (HIGH PRIORITY)
**Location:** `src/transaction/tasks.py:122-208`

**Problem:** `_send_purchase` function is 86 lines with nested logic, multiple responsibilities (validation, seqno management, sending, error handling), difficult to test.

**Why problematic:** Violates Single Responsibility Principle, high cyclomatic complexity, error handling mixed with business logic.

**Suggested fix:** Extract into smaller functions:
- `_validate_purchase_expiry`
- `_prepare_wallet_and_seqno`
- `_build_and_sign_transaction`
- `_broadcast_transaction`
- `_cleanup_on_failure`

---

#### 7. Bare Except Clause (MEDIUM PRIORITY - SECURITY)
**Location:** `src/postgres.py:62-64`

**Problem:**
```python
try:
    yield session
except:  # Bare except catches everything including SystemExit, KeyboardInterrupt
    await session.rollback()
    raise
```

**Why problematic:** Catches `KeyboardInterrupt`, `SystemExit`, makes debugging harder, anti-pattern.

**Suggested fix:** `except Exception:` instead of bare `except:`.

---

#### 8. Inconsistent Naming: "Kiq" vs "Taskiq" (MEDIUM PRIORITY)
**Location:** `src/middlewares.py:39`, `src/worker/_enqueue.py`

**Problem:** Mixed naming - `KiqEnqueuedTasksMiddleware` but uses `taskiq` library.

**Why problematic:** Confusing nomenclature, unclear what "Kiq" refers to.

**Suggested fix:** Rename to `TaskiqEnqueuedTasksMiddleware` for consistency.

---

#### 9. Comment/Code Mismatch in Fragment Cache (EASY FIX)
**Location:** `src/integrations/fragment/main.py:12`

**Problem:**
```python
CACHE_LT = 60 * 5  # 10 mins  <- Comment says 10, but 60*5 = 300 seconds = 5 minutes
```

**Why problematic:** Misleading documentation.

**Suggested fix:** Change to `60 * 10` or update comment to `# 5 mins`.

---

#### 10. Missing Abstraction for Fee Calculations (MEDIUM PRIORITY)
**Location:** `src/fee.py`

**Problem:** Fee calculation logic scattered, no clear separation between TON network fee and API markup.

```python
def after_fee(amount: float) -> float:
    return amount * (1 + settings.API_PRICE_MARKUP)

def after_ton_network_fee(amount: float) -> float:
    return amount + TON_FEE
```

**Why problematic:** Chaining these functions is error-prone, no single source of truth for "total cost".

**Suggested fix:** Create a `FeeCalculator` class with clear methods for different fee types and combined calculations.

---

### B. Poor Separation of Concerns

#### 11. Service Classes as Singletons (MEDIUM PRIORITY)
**Location:** `src/transaction/service.py:217`, `src/deposit/service.py:130`, `src/auth/service.py:100`, `src/user/service.py:114`

**Problem:** Global singleton instances created at module level:
```python
transaction = TransactionService()
deposit = DepositService()
auth = AuthService()
user = UserService()
```

**Why problematic:** Makes testing harder, hides dependencies, not truly stateless despite appearing so.

**Suggested fix:** Use dependency injection or factory pattern, instantiate per-request if needed.

---

#### 12. Business Logic in Task Functions (HIGH PRIORITY)
**Location:** `src/transaction/tasks.py:237-309`

**Problem:** `transactions_log_daily_stats` has complex SQL queries and formatting logic mixed together.

**Why problematic:** Hard to test, SQL logic not reusable, violates Single Responsibility Principle.

**Suggested fix:** Extract statistics gathering into a `StatisticsService` class.

---

#### 13. Mixed Responsibilities in Models (LOW PRIORITY)
**Location:** `src/models/users.py:34-46`

**Problem:** User model has HTML generation methods:
```python
@property
def html_telegram_link(self) -> str:
    return f"<a href='tg://resolve?domain={self.username}'>{html.quote(self.first_name)}</a>"
```

**Why problematic:** Mixing data model with presentation logic.

**Suggested fix:** Move to a separate formatter/presenter class.

---

### C. Configuration & Constants Issues

#### 14. Environment-Based Logic in Module Scope (MEDIUM PRIORITY)
**Location:** `src/wallet/manager.py:8-11`

**Problem:**
```python
if settings.is_production():
    env_network_id = NetworkGlobalID.MAINNET
else:
    env_network_id = NetworkGlobalID.TESTNET
```

**Why problematic:** Executes at import time, harder to test, not explicitly passed to classes that need it.

**Suggested fix:** Pass network_id as parameter to WalletManager constructor.

---

#### 15. Hard-coded Session Key (HIGH PRIORITY - SECURITY)
**Location:** `src/app.py:66`

**Problem:**
```python
fragment_rest_client = FragmentRestClient(
    ton_connect=ton_connect,
    session_key="CanBeAnythingForNow",  # Hard-coded!
)
```

**Why problematic:** Security risk, not configurable, poor practice.

**Suggested fix:** Move to settings or generate dynamically.

---

### D. Performance & Efficiency Issues

#### 16. Potential Logic Error in Chart Data (MEDIUM PRIORITY)
**Location:** `src/transaction/service.py:154-214`

**Problem:** `get_chart_data` builds result by iterating 90 days and looking up in dictionary, but the WHERE clause filters by `TransactionReason.stars` while also selecting both stars AND premium amounts.

```python
.where(
    Transaction.user == user,
    Transaction.reason == TransactionReason.stars,  # Only stars
    # NOTE: might add `Transaction.created_at` to that lol
)
```

**Why problematic:** Logic error - filtering by stars but aggregating premium (will always be 0), misleading query, comment indicates incomplete implementation.

**Suggested fix:** Remove the reason filter or fix the logic to match requirements.

---

#### 17. Inefficient Session Check in Fragment Client (LOW PRIORITY)
**Location:** `src/integrations/fragment/rest_client.py:58-63`

**Problem:** Time-based stale check happens on every API request.

**Why problematic:** Could batch or optimize, adds latency.

**Suggested fix:** Use async background task to refresh session proactively.

---

### E. Code Quality Issues

#### 18. Commented-out Code and TODO Comments (EASY FIX)
**Locations:**
- `src/models/deposits.py:42` - `# can add paid_at here`
- `src/transaction/service.py:187` - `# NOTE: might add Transaction.created_at to that lol`
- `src/app.py:73` - `# does not work without VPN for me`
- `src/transaction/tasks.py:224` - `# PERF: dont forget to change it to > 1 or smth`
- `src/integrations/fragment/rest_client.py:125` - `# sometimes bad text -> "Session expired"`

**Why problematic:** Indicates incomplete work, confusing for maintainers, unprofessional.

**Suggested fix:** Remove comments or create proper tickets/issues.

---

#### 19. Complex Conditional in Transaction Notification (MEDIUM PRIORITY)
**Location:** `src/transaction/tasks.py:224-232`

**Problem:**
```python
if sources_count == 1:  # PERF: dont forget to change it to > 1 or smth
    enqueue_transaction_telegram_log_task(...)
elif sources_count > 1:
    log.warning("...somehow sources number is bigger than 1", ...)
```

**Why problematic:** Comment indicates temporary logic, unclear business requirement.

**Suggested fix:** Clarify business logic, implement proper handling for multiple sources.

---

#### 20. Inconsistent Use of Type Hints (LOW PRIORITY)
**Locations:** Multiple files

**Problem:** Some functions have complete type hints, others are incomplete:
- `src/integrations/fragment/rest_client.py:161` returns `tuple[bool]` but only unpacks one value
- Missing return type hints in some task functions

**Why problematic:** Reduces type safety, makes refactoring riskier.

**Suggested fix:** Add complete type hints throughout codebase.

---

## 2. BUGS AND ISSUES TO FIX

### A. Logic Errors

#### 1. Logic Error in Chart Data Query (CRITICAL)
**Location:** `src/transaction/service.py:168-186`

**Problem:** Query filters by `TransactionReason.stars` but then aggregates both stars and premium amounts - premium will always be 0.

**Fix:** Remove the reason filter or align logic with actual requirements.

---

#### 2. Incorrect Return Type Annotation (MEDIUM)
**Location:** `src/integrations/fragment/rest_client.py:161`

**Problem:**
```python
async def check_ton_proof_auth(self) -> tuple[bool]:
    ...
    return response_data["verified"]  # Returns single bool, not tuple
```

**Fix:** Change return type to `bool`.

---

### B. Missing Error Handling

#### 3. No Validation on Pagination Params (MEDIUM)
**Location:** `src/transaction/service.py:63`, `src/deposit/service.py:26`

**Problem:** No validation that page/limit are positive, could cause DB errors or unexpected behavior.

**Fix:** Add validation in `PaginationParams` or repository layer.

---

#### 4. Missing Error Handling in Fragment Authorization (MEDIUM)
**Location:** `src/integrations/fragment/rest_client.py:113-114`

**Problem:**
```python
await asyncio.sleep(0.5)  # Why? No explanation
await self.check_ton_proof_auth()  # No error handling
```

**Fix:** Add try-except, explain the sleep, validate response.

---

### C. Type Safety Issues

#### 5. Unsafe Dictionary Access (MEDIUM)
**Location:** `src/integrations/fragment/rest_client.py:172`

**Problem:**
```python
return response_data["verified"]  # KeyError if "verified" missing
```

**Fix:** Use `.get()` with default or validate response schema.

---

#### 6. Type Mismatch in Settings (LOW)
**Location:** `src/config.py:68-69`

**Problem:**
```python
ADMIN_TELEGRAM_NOTIFICATIONS_CHAT_ID: int | str = ""  # Empty string default for int|str
ADMIN_TELEGRAM_LOGS_CHAT_ID: int | str = ""
```

**Fix:** Use proper default like `0` or make it optional `int | str | None`.

---

## SUMMARY

### Refactoring Priority:
1. **Critical:** Hard-coded session key (#15), Logic error in chart query (#16)
2. **High:** Duplicate sorting pattern (#1), Inconsistent error handling (#2), Complex transaction logic (#6), Repository pattern inconsistency (#4)
3. **Medium:** Magic numbers (#3), Fee calculation abstraction (#10), Service singletons (#11)
4. **Low/Easy:** Typo in exception name (#5), Comment/code mismatch (#9), TODOs (#18)

### Bug Priority:
1. **Critical:** Chart data logic error, Hard-coded credentials
2. **Medium:** Return type annotation error, Missing validation, Fragment error handling
3. **Low:** Type mismatches, unsafe dictionary access

### Statistics:
- **~20 major refactoring opportunities** identified
- **~6 bugs/issues** to fix
- **Key patterns:** Service layer is well-structured but has duplication, Repository pattern needs standardization, Error handling needs improvement

This codebase is generally well-organized with good async patterns and separation of concerns, but would benefit significantly from addressing the duplication, standardizing the repository pattern, and fixing the hard-coded values.
