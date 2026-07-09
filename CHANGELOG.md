# v1.0.0 Release (Latest, 14.06.2026)

- feat: recipient/buy response `avatar_url` object (with extracted link to avatar)
- refactor: worker (TaskIQ) overhaul
- refactor: changed bot library from `python-telegram-bot` to `aiogram`
- feat: supports multiple API-Keys instead of one
- feat: added [LogTide](https://logtide.dev) observability
- feat: user info sync with telegram
- feat: admin and user transaction logs
- fix: deposits check retry (for when not found sometimes from tonapi) (deposits sometimes didn't worked)
- feat: prettier landing page
- fix: next-i18n causing hydration issues, switched to paraglide

# v1.1.0 (10.07.2026)

- feat: setting (non-ext) transaction hashes after the transaction is send
- [ ] feat: setting transaction hashes for TON deposits
- [ ] feat: redis recipient caching
