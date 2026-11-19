# Landing

Russian-only copy of the landing page in `../web`, including its dark theme,
animations, interactive dashboard demo, pricing, and FAQ.

From `client/`, run `bun run --cwd landing dev` to develop or
`bun run --cwd landing build` to build the static site into `landing/dist`.

The production build prerenders the landing into `dist/index.html`, including
the FAQ answers, so search engines receive the Russian page content without
running JavaScript. The client hydrates that HTML to enable interactions.
The temporary server renderer is removed after the build; hosting stays static.

Links use the same optional `VITE_BOT_USERNAME`, `VITE_REPOSITORY_URL`,
`VITE_DOCS_URL`, `VITE_TELEGRAM_CHAT_URL`, and `VITE_TELEGRAM_CHANNEL_URL`
variables as the web app.

Live totals refresh every 30 seconds from
`${VITE_API_URL}/stats/totals`; the default API base is
`https://api.fragapi.com/v1`. The API must allow the landing's origin through
CORS, or `VITE_API_URL` must point to a same-origin proxy. The current production
API does not return CORS headers. Until configured, the counters show `—`;
failed refreshes retain the last known totals.

Signup buttons preserve UTM parameters and external referrer hostnames through
Telegram login. Share a link such as
`https://fragapi.com/?utm_source=telegram&utm_campaign=november_launch`.
If `utm_medium` is missing, the landing page hostname supplies the medium,
including for untagged visits. You can override it with `utm_medium=channel`.
`utm_campaign` is optional. Without it, the campaign is stored as `NULL` and
the other available fields are still saved for new users.

See [signup attribution](../../server/SIGNUP_ATTRIBUTION.md) for server
configuration, deployment order, and signup counts.
