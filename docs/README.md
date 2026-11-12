# FragAPI docs

Documentation site for FragAPI, served at https://docs.fragapi.com.
Built with [Fumadocs](https://fumadocs.dev) on TanStack Start.

## Development

```bash
bun install
bun run dev # http://localhost:5000
```

## Content

- `content/docs/*.mdx` - hand-written pages. `name.mdx` is Russian (default),
  `name.en.mdx` is English.
- `content/docs/api/**` - one page per API operation, rendered from the
  OpenAPI spec of the server. `content/docs/api/meta.json` sets their order.

## API pages

The pages read the spec from `OPENAPI_URL` (default
`https://api.fragapi.com/openapi.json`), so an endpoint shows up only after
the server with it is deployed.

Titles and descriptions come from the spec: change `summary` / `description`
on the server endpoint, not the `.mdx` file.

To add pages for new endpoints, regenerate them, then check that the new
files are listed in `content/docs/api/meta.json`:

```bash
bun ./scripts/generate-docs.ts
```
