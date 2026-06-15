# Development

The github repository is a mirror of [Forgejo](https://forge.apelsynca.pro/apelsynca/fragapi)
(_You will still be visible as contributor in github_)

If you want to start this locally:

Server: `./server/docker-compose.yml` (has info how to start the server locally) + `./server/.env.template`
Client: `./client/package.json` - (fill .env and do `bun install` + `bun dev`)
Docs: `./docs/package.json` - (just do `bun install` + `bun dev`)

TODOs: (_contributions are welcome, create GH issue first_)

- [ ] Payments view on the client.
- [ ] Redis storage of recipient data for like 5 minutes

---

The rest of the file is unfinished
