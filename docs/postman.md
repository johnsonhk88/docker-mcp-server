# Test the MCP Gateway in Postman

This is the **Postman app** talking to the gateway over HTTP. It is not the same as the **Postman MCP catalog server** (that one uses `postman.postman-api-key` to manage Postman Cloud workspaces).

Keep `oauth: false` on the OpenCode remote config. Postman requests here use Bearer auth only.

## 1. Start the gateway

Follow [usage.md](usage.md) through `docker compose up -d` and a `200` from `/health`.

## 2. Import the collection

1. Open Postman.
2. **Import** → File → `docs/postman/mcp-gateway.postman_collection.json`.
3. Select the collection **Docker MCP Gateway**.
4. On the collection **Variables** tab, set `token` to the same value as `MCP_GATEWAY_AUTH_TOKEN` in `.env`.
5. Leave `baseUrl` as `http://127.0.0.1:8811`.

## 3. Run the requests in order

| Request | What it proves |
| --- | --- |
| **Health** | Gateway is up (no auth) |
| **Initialize** | Bearer works; saves `Mcp-Session-Id` into `sessionId` |
| **List tools** | Catalog tools are visible |
| **Search (DuckDuckGo)** | `tools/call` search |
| **Fetch URL** | `tools/call` fetch |
| **Postman getAuthenticatedUser** | Postman catalog server + API key |

Send **Initialize** before any other `/mcp` request. The collection test script copies `Mcp-Session-Id` into the `sessionId` variable.

Body type is raw JSON. The response is Server-Sent Events (`event: message` then `data: {...}`). That is expected.

## 4. If a request fails

| Symptom | Fix |
| --- | --- |
| `401 Unauthorized` | `token` does not match `.env`, or Bearer header missing |
| Empty or missing session | Run **Initialize** again |
| Postman tool error | Set a real `postman.postman-api-key` and recreate: `docker compose up -d --force-recreate` |
| Connection refused | `docker compose ps` — gateway must be healthy; URL is loopback only |

## 5. Optional: same calls without the collection

See [api-testing.md](api-testing.md) for curl.
