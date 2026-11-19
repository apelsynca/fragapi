# Landing

Russian-only copy of the landing page in `../web`, including its dark theme,
animations, interactive dashboard demo, pricing, and FAQ.

From `client/`, run `bun run --cwd landing dev` to develop or
`bun run --cwd landing build` to build the static site into `landing/dist`.

Links use the same optional `VITE_BOT_USERNAME`, `VITE_REPOSITORY_URL`,
`VITE_DOCS_URL`, `VITE_TELEGRAM_CHAT_URL`, and `VITE_TELEGRAM_CHANNEL_URL`
variables as the web app.

Live totals refresh every 30 seconds from
`${VITE_API_URL}/stats/totals`; the default API base is
`https://api.fragapi.com/v1`. The API must allow the landing's origin through
CORS, or `VITE_API_URL` must point to a same-origin proxy. The current production
API does not return CORS headers. Until configured, the counters show `—`;
failed refreshes retain the last known totals.
