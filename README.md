# Docker MCP Gateway

Run Docker catalog MCP servers behind one Streamable HTTP endpoint so OpenCode can call them.

Gateway servers: **Postman**, **DuckDuckGo** (search), **Fetch** (page to markdown). Optional standalone: **Postman full** (`mcp/postman --full`).

## Docs

- [Step-by-step usage](docs/usage.md) — `.env`, Compose, OpenCode, catalog tools
- [Set up OpenCode](docs/opencode.md) — MCP client config, token export, local vs remote servers
- [Fix HTTP 401 Unauthorized](docs/opencode.md#fix-http-401-unauthorized) — `docker-gateway` Error POSTing to endpoint
- [Test with curl / HTTP API](docs/api-testing.md) — health, initialize, `tools/list`, `tools/call`
- [Test the gateway in the Postman app](docs/postman.md) — import `docs/postman/mcp-gateway.postman_collection.json`
- [Run and test standalone Postman MCP (full)](docs/postman-full.md) — shell setup, stdio tool test, and the `postman-full` OpenCode server

## Requirements

- Docker Engine with Compose
- A [Postman API key](https://go.postman.co/settings/me/api-keys) for the Postman server

## Setup

```bash
cp .env.example .env
```

Edit `.env`:

1. Set `MCP_GATEWAY_AUTH_TOKEN` to a long random string (same value OpenCode will send).
2. Set `postman.postman-api-key` to your Postman API key.

```bash
docker compose up -d
```

Check the gateway:

```bash
curl -sS http://127.0.0.1:8811/health
```

The MCP endpoint is `http://127.0.0.1:8811/mcp`. It requires:

```http
Authorization: Bearer <MCP_GATEWAY_AUTH_TOKEN>
```

The published port is bound to `127.0.0.1` only.

## OpenCode

Full walkthrough: [Set up OpenCode](docs/opencode.md).

This repo includes `opencode.jsonc`. OpenCode reads `{env:MCP_GATEWAY_AUTH_TOKEN}` from **your shell environment**, not from `.env`.

```bash
export MCP_GATEWAY_AUTH_TOKEN='the-same-token-as-in-.env'
opencode mcp list
```

You want `docker-gateway` **connected**. Keep `oauth: false` — this gateway uses a Bearer token, not OAuth.

If you see **Error POSTing to endpoint: Unauthorized (HTTP 401)**, see [Fix HTTP 401 Unauthorized](docs/opencode.md#fix-http-401-unauthorized).

To use it from every project, copy the `mcp.servers.docker-gateway` block into `~/.config/opencode/opencode.jsonc`.

## Standalone Postman full server (optional)

The gateway's Postman server provides the catalog toolset. For the full 100+ tool set, `opencode.jsonc` also defines a local stdio server named `postman-full`.

```bash
scripts/setup-postman-mcp.sh
opencode mcp list
```

`setup-postman-mcp.sh` reads `postman.postman-api-key` from `.env`, pulls `mcp/postman`, and verifies the MCP handshake. You want `postman-full` **connected** in OpenCode. Its tools are prefixed `postman_full_*`; gateway tools are `docker_gateway_*`.

Full guide, tool-call test, and troubleshooting: [Run and test standalone Postman MCP (full)](docs/postman-full.md).

## Test

```bash
# Gateway health: expect 200
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8811/health

# Standalone Postman MCP: expect "OK: Postman MCP --full responded"
scripts/setup-postman-mcp.sh

# OpenCode connections: expect docker-gateway and postman-full connected
opencode mcp list
```

More: [curl/HTTP API](docs/api-testing.md), [Postman app](docs/postman.md), [standalone Postman full](docs/postman-full.md).

## Add another catalog server

1. Find the server name on [Docker MCP Catalog](https://hub.docker.com/mcp/explore).
2. Append it to `--servers=` in `compose.yaml` (comma-separated), for example:

   `--servers=postman,duckduckgo,fetch,playwright`

3. If the server needs a secret, add `server.secret-name=value` to `.env` (see the catalog Config tab).
4. Recreate the gateway:

   ```bash
   docker compose up -d --force-recreate
   ```

Crawl4AI is not in the Docker catalog; do not add it here. Use a separate Compose service later if you need it.

## Secrets

- `.env` is gitignored. Never commit it.
- `.env.example` is the template only.
- Compose mounts `.env` into the gateway as `/run/secrets/mcp_secrets`.

## Stop

```bash
docker compose down
```
