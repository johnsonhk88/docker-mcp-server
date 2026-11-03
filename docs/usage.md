# Use the MCP Gateway

Step-by-step: start the gateway, connect OpenCode, and call catalog tools.

## 1. Requirements

- Docker Engine with Compose
- OpenCode (optional, for agent use)
- A [Postman API key](https://go.postman.co/settings/me/api-keys) if you want Postman Cloud tools

## 2. Create `.env`

From the repo root:

```bash
cp .env.example .env
```

Edit `.env`:

1. Set `MCP_GATEWAY_AUTH_TOKEN` to a long random value, for example:

   ```bash
   openssl rand -hex 32
   ```

2. Set `postman.postman-api-key` to your Postman API key (`PMAK-...`).

Never commit `.env`.

## 3. Start the gateway

```bash
docker compose up -d
docker compose ps
```

Wait until the `gateway` service is **healthy**. First start can take a minute while catalog images pull.

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8811/health
```

Expect `200`. The MCP URL is `http://127.0.0.1:8811/mcp` (loopback only).

If you changed `.env` after a previous start:

```bash
docker compose up -d --force-recreate
```

## 4. Connect OpenCode

Full walkthrough (project config, global config, CLI, other MCP servers): [Set up OpenCode](opencode.md).

OpenCode does **not** read Compose `.env`. Export the same token in the shell that starts OpenCode:

```bash
export MCP_GATEWAY_AUTH_TOKEN='the-same-token-as-in-.env'
```

This repo already has `opencode.jsonc`. Start OpenCode in this directory, then:

```bash
opencode mcp list
```

You want `docker-gateway` **connected**. Keep `oauth: false` in that config. The gateway uses a Bearer token, not OAuth.

If `mcp list` shows **Unauthorized (HTTP 401)**, see [Fix HTTP 401 Unauthorized](opencode.md#fix-http-401-unauthorized).

## 5. What you can call

The gateway exposes one MCP endpoint. Behind it:

| Catalog server | Typical tools | Needs |
| --- | --- | --- |
| Postman | `getWorkspaces`, `getCollections`, `runCollection`, … | `postman.postman-api-key` |
| DuckDuckGo | `search`, `fetch_content` | none |
| Fetch | `fetch` (URL → markdown) | none |

Ask OpenCode to search the web, fetch a page, or list your Postman workspaces. Tool names appear as `docker_gateway_<tool>` in OpenCode.

## 6. Optional: standalone Postman full server

The gateway's Postman server covers the catalog toolset. For the full 100+ tool set, the repo also defines a local stdio server named `postman-full`. It coexists with the gateway:

```bash
scripts/setup-postman-mcp.sh
opencode mcp list
```

You want both `docker-gateway` and `postman-full` connected. Tools are prefixed `postman_full_*`. Setup, tool-call test, and troubleshooting: [Run and test standalone Postman MCP (full)](postman-full.md).

## 7. Add another catalog server

1. Find the name on the [Docker MCP Catalog](https://hub.docker.com/mcp/explore).
2. Append it to `--servers=` in `compose.yaml`, comma-separated:

   `--servers=postman,duckduckgo,fetch,playwright`
3. If the catalog Config tab lists a secret, add `server.secret-name=value` to `.env`.
4. Recreate:

   ```bash
   docker compose up -d --force-recreate
   ```

Crawl4AI is not in the Docker catalog. Do not add it here.

## 8. Stop

```bash
docker compose down
```

## Next

- [Set up OpenCode](opencode.md)
- [Test with curl / HTTP API](api-testing.md)
- [Test with the Postman app](postman.md)
- [Run and test standalone Postman MCP full](postman-full.md)
