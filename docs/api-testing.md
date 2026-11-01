# Test the MCP Gateway over HTTP

The gateway speaks **MCP Streamable HTTP** at `http://127.0.0.1:8811/mcp`. Responses are `text/event-stream` (`event: message` + `data: {jsonrpc...}`).

Set the token once:

```bash
export MCP_GATEWAY_AUTH_TOKEN='the-same-token-as-in-.env'
export MCP_URL=http://127.0.0.1:8811
```

## 1. Health (no auth)

```bash
curl -sS -o /dev/null -w "%{http_code}\n" "$MCP_URL/health"
```

Expect `200` and an empty body.

## 2. MCP rejects missing Bearer

```bash
curl -sS -o /dev/null -w "%{http_code}\n" -X POST "$MCP_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect `401`.

## 3. Initialize (get a session)

Every later MCP call needs the `Mcp-Session-Id` header from this response.

```bash
curl -sS -D - -X POST "$MCP_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Authorization: Bearer ${MCP_GATEWAY_AUTH_TOKEN}" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect `200`, header `Mcp-Session-Id: …`, and SSE JSON whose `serverInfo.name` is `Docker AI MCP Gateway`.

Copy the session id:

```bash
export MCP_SESSION='paste-Mcp-Session-Id-here'
```

## 4. List tools

```bash
curl -sS -X POST "$MCP_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Authorization: Bearer ${MCP_GATEWAY_AUTH_TOKEN}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

Expect tools including `search`, `fetch`, `fetch_content`, and Postman tools such as `getWorkspaces`.

## 5. Call a tool (web search)

```bash
curl -sS -X POST "$MCP_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Authorization: Bearer ${MCP_GATEWAY_AUTH_TOKEN}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search","arguments":{"query":"MCP streamable HTTP","max_results":3}}}'
```

Expect `result.content` with search hits.

## 6. Call Fetch (page to markdown)

```bash
curl -sS -X POST "$MCP_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Authorization: Bearer ${MCP_GATEWAY_AUTH_TOKEN}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"fetch","arguments":{"url":"https://example.com"}}}'
```

## 7. Call a Postman catalog tool

Needs a real `postman.postman-api-key` in `.env`.

```bash
curl -sS -X POST "$MCP_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Authorization: Bearer ${MCP_GATEWAY_AUTH_TOKEN}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"getAuthenticatedUser","arguments":{}}}'
```

## Headers that matter

| Header | When |
| --- | --- |
| `Authorization: Bearer <token>` | Every `/mcp` request |
| `Accept: application/json, text/event-stream` | Every `/mcp` request |
| `Content-Type: application/json` | POST body |
| `Mcp-Session-Id` | After initialize |

`/health` needs none of these.

To click through the same calls in the Postman app, see [postman.md](postman.md).
