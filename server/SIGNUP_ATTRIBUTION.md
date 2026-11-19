# Signup attribution

Both landing pages capture `utm_source`, `utm_medium`, and `utm_campaign`.
An external referrer hostname is saved when available; it supplies the source
when `utm_source` is absent. Referrer paths and query strings are discarded.
The first visit, including an unattributed visit, is retained in localStorage
for 30 days. Storage is per browser and origin; if storage is blocked, it lasts
only for the current page. Browsers may suppress referrers, so untagged traffic
cannot always be identified.

The standalone landing page uses its hostname when `utm_medium` is missing,
including on untagged visits. `utm_campaign` is optional and is stored as
`NULL` when absent.

Example campaign link:

```text
https://fragapi.com/?utm_source=telegram&utm_medium=channel&utm_campaign=november_launch
```

Attributed login buttons navigate to `GET /v1/attribution/start`. This public
endpoint saves a random token in Redis for 30 days and redirects to the bot with
`start=login_a_<token>`. No browser fetch or CORS configuration is needed.
Responses are not cached. Token storage/resolution is bounded to one second;
Redis errors, missing tokens, and corrupt tokens fall back to normal login.
The tokens carry marketing metadata only and do not authenticate anyone.

At user creation, metadata is saved in `users.signup_source`, `signup_medium`,
`signup_campaign`, and `signup_referrer`, and appended to the existing “New user”
admin notification. The structured `New user` log includes the same `signup_*`
fields. Existing users are never backfilled and later logins never overwrite
signup attribution. These fields count signups, not visits or conversions.

## Deployment

Run `uv run task db_migrate` from `server/` before starting the updated server or
worker. The Docker pre-deploy command already does this. Deploy the server
before the landing pages.

Set `FRAG_BOT_USERNAME` on the server to match the clients' `VITE_BOT_USERNAME`
(both default to `frag_api_bot`). On both clients, `VITE_API_URL` is the public
API base including `/v1`, defaulting to `https://api.fragapi.com/v1`. Set it at
build time for other deployments; a same-origin `/v1` proxy is also supported.

For direct Telegram campaigns, configure a JSON mapping in the server environment:

```dotenv
FRAG_SIGNUP_CAMPAIGNS={"channel_november":{"source":"telegram","medium":"channel","campaign":"november_launch"}}
```

Then share `https://t.me/frag_api_bot?start=src_channel_november`.
These links open the normal bot menu and attribute new users. Mapping keys must
use letters, digits, underscores, or hyphens and fit in the 64-character Telegram
start payload including the `src_` prefix. Unknown or invalid campaigns are
ignored. Keep mappings stable while links are in use.

To inspect acquisition counts:

```sql
SELECT signup_source, signup_medium, signup_campaign, count(*) AS signups
FROM users
GROUP BY signup_source, signup_medium, signup_campaign
ORDER BY signups DESC;
```

Run the targeted checks with:

```sh
# server/
FRAG_ENV=testing uv run pytest tests/attribution tests/bot/menu tests/auth tests/test_openapi.py
# client/web/
bun x vitest run src/lib/signup-attribution.test.ts
```
