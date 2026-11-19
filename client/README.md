# Client workspace

Run `bun install` from this directory to install all workspace dependencies.
Run `bun run --cwd web dev` to develop the web app.
New packages such as `landing/` and `ui/` can be added with their own
`package.json`; the root workspace includes all immediate subdirectories.

## Railway

For the web service, use the Railpack builder and configure:

- Root Directory: `/client`
- Service variable: `RAILPACK_CONFIG_FILE=railpack.web.json`

The config installs dependencies from the workspace root, builds `web/`, and
starts its Nitro server using Node.js 24. Railway supplies the `PORT` variable.

Alternatively, omit the config selection and set these service variables:

```sh
RAILPACK_BUILD_CMD="bun run --cwd web build"
RAILPACK_START_CMD="node web/.output/server/index.mjs"
```

Each additional app can have its own Railpack config or command variables while
keeping `/client` as its Root Directory.

For the landing service, use the Railpack builder and configure:

- Root Directory: `/client`
- Service variable: `RAILPACK_CONFIG_FILE=railpack.landing.json`
- Service variable: `RAILPACK_SPA_OUTPUT_DIR=landing/dist`

The config installs dependencies from the workspace root and builds `landing/`.
Railpack serves the built static files with Caddy. Leave the service's custom
start command unset so Railpack can configure the static server.
