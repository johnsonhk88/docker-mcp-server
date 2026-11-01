# Docker MCP Gateway

Run Docker catalog MCP servers behind one Streamable HTTP endpoint so OpenCode can call them.

v1 servers: **Postman**, **DuckDuckGo** (search), **Fetch** (page to markdown).

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

This repo includes `opencode.jsonc`. OpenCode reads `{env:MCP_GATEWAY_AUTH_TOKEN}` from **your shell environment**, not from `.env`.

```bash
export MCP_GATEWAY_AUTH_TOKEN='the-same-token-as-in-.env'
```

Then start OpenCode in this directory, or copy the `mcp.servers.docker-gateway` block into `~/.config/opencode/opencode.jsonc`.

```sh
opencode mcp list
```

You want `docker-gateway` **connected**. If it is not, confirm Compose is up and the exported token matches `.env`.

To add the server globally instead:

```sh
opencode mcp add docker-gateway --global --url http://127.0.0.1:8811/mcp --header 'Authorization=Bearer {env:MCP_GATEWAY_AUTH_TOKEN}'
```

Remote OAuth is off; this gateway uses the Bearer token, not Postman OAuth.

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
