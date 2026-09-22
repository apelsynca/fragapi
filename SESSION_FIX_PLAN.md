# SESSION / AUTH FIX PLAN

> **Implementation status (Sep 2026):**
>
> | Phase | Item | Status |
> |---|---|---|
> | 1 | Client cookie `maxAge` (7d) + `SameSite=Lax` | ✅ done in `client/src/lib/session.ts` |
> | 2 | `beforeLoad` throws `redirect` directly; no more `errorComponent` hack | ✅ done in `client/src/routes/dashboard/route.tsx` |
> | 2 | Friendly "Session expired" error component for open tabs | ✅ done in `client/src/routes/dashboard/route.tsx` (`SessionExpired`) |
> | 3 | `apiRequest` JSON guard, status-based 401, conditional body, 15s timeout, `ApiError` class | ✅ done in `client/src/server-api/request.ts` |
> | 4 | Structured `botHashLoginFn` result + friendly expired/invalid link page | ✅ done in `client/src/server-api/auth-manager.ts` and `client/src/routes/bot-login.tsx` |
> | 5 | Server sliding expiration (throttled, 1h refresh window) | ✅ done in `server/src/auth/service.py` (`_maybe_slide_expiration`) |
> | 5 | Removed stale `# WARN` comment; demoted per-request auth log to `debug` | ✅ done in `server/src/auth/service.py` and `server/src/auth/middlewares.py` |
> | 6 | `await session.clear()` in `logoutFn` | ✅ done in `client/src/server-api/auth-manager.ts` |
> | 6 | `queryClient.clear()` instead of `invalidateQueries()` on logout | ✅ done in `client/src/components/AppSidebar/AppSidebarBottom.tsx` |
> | 6 | `onError` toasts on API-token create/delete mutations | ✅ done in `client/src/components/ApiTokens/CreateApiTokenDialog.tsx` and `ApiTokenCard.tsx` |
> | 6 | Unify `redirect({ to: ... })` (drop `href`) | ✅ done in `client/src/lib/auth.ts` |
>
> Not yet addressed (deliberately): stricter `maxAge`/`sameSite` hardening
> (`__Host-start` cookie name), TanStack CSRF middleware, `staleTime`
> adjustment, new `FRAG_USER_SESSION_TTL`/`SESSION_REFRESH_THRESHOLD`
> `.env.template` entries, and full CI/test matrix. See "Not yet done" at the
> bottom for details.

Investigation of the "session dies after ~12h and dashboard shows an error"
bug, plus every other auth-related defect found along the way.
Scope: `client/` (TanStack Start) and `server/` (FastAPI).

---

## 0. TL;DR

There are **two independent bugs** that combine into the reported symptom:

1. **The session cookie has no `Max-Age`** — it is a *browser session cookie* and
   dies the moment the browser process exits (overnight ≈ "12± hours").
   `client/src/lib/session.ts:8`
2. **When the session is gone, the dashboard shows a raw error instead of
   redirecting** — because `errorComponent` throws a `redirect()`, which the
   router does **not** handle during render.
   `client/src/routes/dashboard/route.tsx:13-19`

The backend session token itself lives **7 days** (`server/src/config.py:48`), so
the backend is *not* the part that dies first.

---

## 1. How auth works today (map)

```
Telegram bot  →  login link  PANEL_URL/bot-login?hash=<bot_hash>
                                  │
                                  ▼
client server fn  botHashLoginFn ── POST /v1/auth/tgbot ──► server: login_by_bot_hash()
(client/src/server-api/auth-manager.ts)                        server/src/auth/service.py
   │  exchanges one-time bot_hash (15 min TTL) for a `pses_*` token (7 day TTL)
   │  stores it in an iron-sealed cookie session:
   ▼
h3 useSession (name: "start", password: SESSION_PASSWORD)      client/src/lib/session.ts
   │  cookie sealed with iron-webcrypto, ttl 0
   ▼
every dashboard server fn (fetchMe, fetchTransactionsPage, ...)
   calls verifySession() → reads cookie → Bearer token → backend           client/src/lib/auth.ts
```

Guards:
- `__root.tsx` `beforeLoad` → `fetchSessionToken()` → `context.token`
- `/dashboard` `beforeLoad` → throws `Error('Not authenticated')` if no token
- `apiRequest()` auto-`logoutFn()` when backend answers `{"error": "Unauthorized"}`

---

## 2. Root cause of the reported bug

### 2.1 Session cookie is a browser-session cookie (the "12 hours" part)

`client/src/lib/session.ts`:

```ts
return useSession<SessionUser>({ password: process.env.SESSION_PASSWORD! })
```

No `maxAge` is passed. Verified in `h3` (the session impl TanStack Start wraps,
`node_modules/h3/dist/h3.mjs`):

```js
// updateSession():
setChunkedCookie(event, sessionName, sealed, {
  ...DEFAULT_SESSION_COOKIE,                       // { path, secure, httpOnly } — no maxAge!
  expires: config.maxAge ? new Date(...) : void 0, // undefined → no Expires attribute
})
// sealSession():
ttl: config.maxAge ? config.maxAge * 1e3 : 0       // 0 → seal never expires cryptographically
```

Consequences:
- The `start` cookie is serialized **without `Max-Age`/`Expires`** → the browser
  treats it as a session cookie and **deletes it when the browser closes**.
  Browser/OS restart overnight → "session died after ~12h".
- Ironically the sealed blob never expires cryptographically, and the backend
  token would still be valid for 7 days — only the cookie is gone.

### 2.2 Dead session → error screen instead of redirect (the "error" part)

`client/src/routes/dashboard/route.tsx`:

```tsx
beforeLoad: ({ context }) => {
  if (!context.token) {
    throw new Error('Not authenticated')      // plain Error, not a redirect
  }
},
errorComponent: ({ error }) => {
  if (error.message === 'Not authenticated') {
    throw redirect({ to: '/' })               // ← broken pattern
  }
  throw error
},
```

A `redirect()` thrown **during render** (from `errorComponent`) is *not*
special-cased by the router — verified in
`@tanstack/react-router/src/CatchBoundary.tsx` (no `isRedirect` handling) and
`Match.tsx` (redirects are only handled for `match.status === 'redirected'`,
i.e. errors thrown during **load**). The render-time throw bubbles up to the
root `errorComponent` → user sees the default **"Something went wrong!"**
screen.

The same failure mode hits an **already-open tab** after the cookie dies /
backend 401s:
1. Queries refetch → `verifySession()` throws `redirect` inside the server fn
   (client/src/lib/auth.ts:23), or `apiRequest()` calls `logoutFn()`
   (client/src/server-api/request.ts:30).
2. The redirect error is re-thrown into the react-query `queryFn`
   (`start-client-core` `serverFnFetcher.ts`).
3. `useSuspenseQuery` throws it into the route error boundary.
   Child routes (`/dashboard/`, `/dashboard/transactions`, …) define **no
   `errorComponent`** → default "Something went wrong!" screen.
   (The `router-ssr-query` integration does install a `queryCache.onError`
   that navigates to `/`, but the suspense error renders first → error flash
   or stuck error page.)

So the user gets an error page in ~all session-death scenarios.

---

## 3. Fix plan

### Phase 1 — P0: make the session cookie persistent (fixes the 12h bug)

**`client/src/lib/session.ts`**

```ts
export const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7 // keep in sync with server USER_SESSION_TTL

export function useAppSession() {
  return useSession<SessionUser>({
    password: process.env.SESSION_PASSWORD!,
    maxAge: SESSION_MAX_AGE_SECONDS,     // ← sets cookie Max-Age AND seal ttl
    cookie: { sameSite: 'lax' },          // make intent explicit (browser default today)
    name: 'frag-session',                 // explicit, chunked-cookie prefix will be frag-session.*
  })
}
```

Notes:
- `maxAge` covers both the cookie lifetime and the iron seal TTL (see h3 code
  above), so an old sealed cookie can no longer be replayed forever either.
- Add a **fail-fast startup check** for `SESSION_PASSWORD` (missing / < 32 chars
  — iron's `minPasswordlength`) instead of the silent `!` non-null assertion.
- Keep the client `maxAge` and server `USER_SESSION_TTL` in sync — ideally one
  value documented in both `.env.template`s.

Effort: ~15 min. Risk: low (existing cookies become irrelevant only after 7d).

### Phase 2 — P0: correct redirect flow (fixes the error screens)

**`client/src/routes/dashboard/route.tsx`** — throw the redirect directly in
`beforeLoad`, delete the `errorComponent` hack:

```tsx
beforeLoad: ({ context, location }) => {
  if (!context.token) {
    throw redirect({
      to: '/',
      search: { sessionExpired: true },   // optional: landing shows "re-login via bot" toast
    })
  }
},
```

Redirects thrown in `beforeLoad`/loaders are handled natively by the router
(this is the documented guard pattern — see the bundled
`router-core/skills/auth-and-guards` skill).

**Session-death while the tab is open:**
- Option A (recommended, small): keep `verifySession()`'s redirect; add a
  shared `errorComponent` on the `/dashboard` layout (and/or set
  `router.defaultErrorComponent`) that renders a friendly
  "Session expired — open the bot to log in again" panel for redirect errors
  instead of the raw default. The ssr-query `queryCache.onError` navigation
  still fires and will move the user to `/`.
- Option B: in `queries.ts` add `throwOnError: (err) => isRedirect(err)` … not
  needed; Option A suffices.

**`client/src/routes/bot-login.tsx`** — stop throwing redirects out of the
login server fn; return a result and render a proper page:

- `botHashLoginFn` (auth-manager.ts): on backend 404/`success !== true`, return
  `{ ok: false, reason: 'expired' | 'invalid' }` instead of
  `throw redirect({ to: '/' })` (the two `NOTE` comments in the file already
  beg for this).
- `bot-login.tsx` loader: on `ok: false` render an inline
  "Login link expired — open @bot to get a new one" page (link via
  `VITE_BOT_USERNAME`); remove the `'No hash broo'` copy.

Effort: ~1–2 h incl. manual verification.

### Phase 3 — P1: harden `apiRequest` (auth-adjacent crashes)

**`client/src/server-api/request.ts`** — current issues:

| Issue | Line | Effect |
|---|---|---|
| `await response.json()` unguarded | 23 | Backend 5xx HTML / proxy 502 / empty 204 → `TypeError: … JSON` → raw error screen, no logout, no toast |
| Logout only when `error === 'Unauthorized'` | 29 | Any 401 with a different/empty body skips logout → user stuck until reload |
| `body: JSON.stringify(data.payload)` always set | 20 | `GET`/`DELETE` with `payload: null` → `body: "null"` → fetch `TypeError` (currently latent; all GET calls happen to omit `payload`) |
| `JSON.stringify(detail)` in message | 33 | Double-encoded detail (`"{\"...\": ...}"` shown to users) |
| no timeout | — | Hung backend hangs the server fn / SSR |
| `logoutFn()` throws redirect mid-handler | 30–31 | Surfaces as a query error (Phase 2 mitigates the UX) |

Fix sketch:

```ts
const json = await response
  .json()
  .catch(() => null)                       // never crash on non-JSON

if (!response.ok) {
  if (response.status === 401 && data.token) {
    await logoutFn()                        // status-based, not body-based
  }
  throw new ApiError(json?.error ?? `HTTP ${response.status}`, json?.detail)
}

// body only when present:
...(data.payload != null ? { body: JSON.stringify(data.payload) } : {}),
signal: AbortSignal.timeout(15_000),
```

Introduce a small `ApiError` class (name, detail, status) so components can
distinguish auth vs. network vs. validation errors.

Effort: ~1 h.

### Phase 4 — P1 (server): session lifecycle improvements

1. **Sliding expiration** — `server/src/auth/service.py:47` `authenticate()`
   only *reads*; `expires_at` is fixed at login for `USER_SESSION_TTL` (7d).
   An active user is logged out at day 7 regardless of activity. Recommended:
   on successful authenticate, bump
   `user_session.expires_at = utc_now() + settings.USER_SESSION_TTL`
   (cheap UPDATE, keeps active users logged in; cron still cleans idle ones).
2. **Stale/misleading comment** — `service.py:23`
   `# WARN: expires_at somehow not checking` is wrong: the filter
   `UserSession.expires_at > utc_now()` on line 25 *is* the check. Delete the
   comment (it misleads future readers).
3. **Log noise** — `server/src/auth/middlewares.py:85` logs
   `"Authenticated subject"` at INFO on **every** request. Demote to `debug`
   (or log only anonymous/failed).
4. Optional hardening: cap concurrent `UserSession` rows per user, and expose
   `FRAG_USER_SESSION_TTL` in `.env.template` so ops knows it exists.

Effort: ~1–2 h (incl. a small pytest for sliding expiry in `server/tests`).

### Phase 5 — P2: auth UX polish

1. **Silent mutation failures** — `CreateApiTokenDialog.tsx`,
   `ApiTokenCard.tsx` mutations have `onSuccess` toasts but **no `onError`**
   (a 401/500 there is completely silent). Add `onError` toasts (reuse
   `ApiError` message from Phase 3).
2. **`logoutFn`** (`auth-manager.ts:36-42`): `session.clear()` not awaited;
   add `await`. Also `queryClient.invalidateQueries()` in
   `AppSidebarBottom.tsx:54` re-triggers fetches on a route that is about to
   unmount — use `queryClient.clear()` (or `removeQueries`) so no stale
   dashboard data flashes for the next (unauthenticated) visitor.
3. **Redirect style unification** — mix of `redirect({ href: '/' })`
   (auth.ts, auth-manager.ts) and `redirect({ to: '/' })` (bot-login.tsx).
   Prefer typed `to:` everywhere; while at it give verifySession a
   `sessionExpired` search flag (Phase 2).
4. **`bot-login.tsx:22` comment** "should throw redirect on success" is
   wrong — the fn *resolves* on success and the *loader* throws. Fix comment
   or (better) make the loader read the structured result from Phase 2.
5. **`queries.ts` / `query.ts`**: `staleTime: 15s` is aggressive for
   dashboard stats; consider 60s+ to reduce refetch storms on refocus
   (also lowers the blast radius of an expired session).

---

## 4. Verification checklist

Manual (client, `bun run dev` + server):
- [ ] Fresh login via bot → devtools shows `frag-session` cookie with
      `Max-Age=604800; HttpOnly; Secure; SameSite=Lax`.
- [ ] Fully close & reopen the browser → `/dashboard` still authorized.
- [ ] Simulate expiry: temporarily set `maxAge: 5` (client) → after ~5s,
      reload `/dashboard` → lands on `/` (or expired page), **no** error
      component, no "Something went wrong!".
- [ ] Simulate backend 401: stop postgres / shorten `USER_SESSION_TTL` →
      open dashboard tab → friendly "session expired" state, auto-redirect,
      no raw error.
- [ ] Stop backend entirely (proxy 502) → dashboard shows a toast/panel, not
      a crash (Phase 3).
- [ ] `/bot-login?hash=garbage` → friendly "link expired" page, not error.
- [ ] Logout → landing, no stale data flash, cookie deleted
      (`Set-Cookie` with empty value / `Max-Age=0`).

Server:
- [ ] `uv run pytest` (existing suite) green.
- [ ] New test: sliding expiration (authenticate at t, assert `expires_at`
      moved forward) — if Phase 4.1 implemented.

---

## 5. Suggested order & owners

| # | Change | Priority | Files |
|---|---|---|---|
| 1 | Cookie `maxAge` + startup validation | P0 | `client/src/lib/session.ts` |
| 2 | Real redirect in `beforeLoad`, remove errorComponent hack | P0 | `client/src/routes/dashboard/route.tsx` |
| 3 | Friendly session-expired handling for open tabs | P0 | dashboard layout / root error component |
| 4 | `apiRequest` robustness (JSON guard, 401-by-status, conditional body, timeout) | P1 | `client/src/server-api/request.ts` |
| 5 | Structured bot-login result + expired-link page | P1 | `client/src/server-api/auth-manager.ts`, `client/src/routes/bot-login.tsx` |
| 6 | Sliding session expiration + comment/log cleanup | P1 | `server/src/auth/service.py`, `middlewares.py` |
| 7 | Mutation `onError` toasts, logout cache clear, `to:` unification | P2 | `CreateApiTokenDialog.tsx`, `ApiTokenCard.tsx`, `AppSidebarBottom.tsx`, `auth.ts` |

---

## 6. Explicitly *not* problems (checked, no action needed)

- Backend `USER_SESSION_TTL` (7d) and the daily `auth.delete_expired` cron
  (`00:15`) are consistent; expired-but-undeleted rows are still rejected by
  `authenticate()` (the `expires_at > utc_now()` filter works — despite the
  stale WARN comment).
- `BOT_LOGIN_SESSION_TTL` (15 min) only affects one-time bot login links —
  by design.
- `.env` files are gitignored (verified `git ls-files`) — not committed.
- Token is stored in an HttpOnly iron-sealed cookie, not localStorage — good.
- SameSite: browser default (Lax) already blocks cross-site POST server-fn
  calls with the cookie; explicit `sameSite: 'lax'` in Phase 1 just documents
  it. (If stricter posture is wanted later: TanStack's `createCsrfMiddleware`
  or `sameSite: 'strict'` — note 'strict' would break the Telegram-in-app
  browser deep-link into `/bot-login`, so Lax is correct here.)

---

## 7. Not yet done (follow-ups)

- **Startup validation of `SESSION_PASSWORD`** (fail fast on missing / < 32
  chars) — the non-null assertion still silently produces an empty password.
- **`.env.template` entries** for `SESSION_PASSWORD`, `SESSION_MAX_AGE` and
  `FRAG_USER_SESSION_TTL` so ops knows they exist and stay in sync.
- **`__Host-` cookie prefix** (requires HTTPS in dev) and TanStack's
  `createCsrfMiddleware` — defense in depth; not strictly needed while the
  cookie is `SameSite=Lax` and `HttpOnly`.
- **`staleTime`/`gcTime` tuning** in `client/src/lib/query.ts` (still 15s/15m).
- **Dedicated sliding-expiration pytest** (verify `_maybe_slide_expiration`
  renews once inside the 1h threshold and skips otherwise).
- Pre-existing, out of scope: `tsconfig.json` `baseUrl` deprecation warning
  under TS 6 (`tsc --noEmit` needs `--ignoreDeprecations 6.0` until nitro's
  base config is updated).
