# v1.0.0 Beta (Latest)

- feat: recipient/buy response `avatar_url` object (with extracted link to avatar)
- refactor: worker (TaskIQ) overhaul
- refactor: changed bot library from `python-telegram-bot` to `aiogram`
- feat: supports multiple API-Keys instead of one
- feat: added [LogTide](https://logtide.dev) observability
- feat: user info sync with telegram
- feat: admin and user transaction logs
- fix: deposits check retry (for when not found sometimes from tonapi) (deposits sometimes didn't worked)
- feat: prettier landing page
