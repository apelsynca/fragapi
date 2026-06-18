# Development

The github repository is a mirror of [Forgejo repository](https://forge.apelsynca.pro/apelsynca/fragapi)
(_You will still be visible as contributor in github_)

If you want to start this locally:

Server: `./server/docker-compose.yml` (has info how to start the server locally) + `./server/.env.template`
Client: `./client/package.json` - (fill .env and do `bun install` + `bun dev`)
Docs: `./docs/package.json` - (just do `bun install` + `bun dev`)

---

The rest of the file is unfinished

---

Commit names (allowed to combine):

feat - you've added something new in the commit! (hope added in prev/next commit tests aswell)
fix - something was broken, and you fixed it in commit.
tests - you've added more tests.
refactor - you've changed the code (making it better/faster/prettier) without changing the logic.
docs - changes in the docs/readme's

---
