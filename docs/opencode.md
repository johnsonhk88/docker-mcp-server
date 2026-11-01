# Set up OpenCode with this MCP gateway

OpenCode is an MCP **client**. This repo is an MCP **server** (Docker MCP Gateway). Wire them together so agents can call Postman, DuckDuckGo, and Fetch through one Streamable HTTP endpoint.

Official OpenCode reference: [MCP servers](https://opencode.ai/v2/docs/mcp-servers) (V2). Config reloads on save; you do not need to restart OpenCode.

## 1. Start the gateway

Follow [usage](usage.md) through health check. You need:

- Compose up, `http://127.0.0.1:8811/health` returning `200`
- The same `MCP_GATEWAY_AUTH_TOKEN` in `.env` that OpenCode will send

The MCP URL is `http://127.0.0.1:8811/mcp` (loopback only). It requires:

```http
Authorization: Bearer <MCP_GATEWAY_AUTH_TOKEN>
```

## 2. Export the token for OpenCode

OpenCode does **not** read Compose `.env`. `{env:MCP_GATEWAY_AUTH_TOKEN}` comes from the **shell environment** of the process that starts OpenCode.

```bash
export MCP_GATEWAY_AUTH_TOKEN='the-same-token-as-in-.env'
```

Put that export in `~/.bashrc` / `~/.zshrc` if you want it every session.

## 3. Project config (this repo)

This repo already has `opencode.jsonc`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "docker-gateway": {
        "type": "remote",
        "url": "http://127.0.0.1:8811/mcp",
        "oauth": false,
        "headers": {
          "Authorization": "Bearer {env:MCP_GATEWAY_AUTH_TOKEN}",
        },
      },
    },
  },
}
```

Keep `oauth: false`. Remote servers default to OAuth; this gateway uses a Bearer token, not OAuth.

Start OpenCode from this directory so it picks up that file.

## 4. Verify

```sh
opencode mcp list
```

You want `docker-gateway` **connected**. In OpenCode, `/mcps` also lists servers and lets you connect or disconnect.

If it is not connected:

1. Gateway healthy? `curl -sS http://127.0.0.1:8811/health`
2. Token exported in **this** shell, and equal to `.env`?
3. `oauth` still `false`?

## 5. Use it from every project (global)

Copy the `mcp.servers.docker-gateway` block into `~/.config/opencode/opencode.jsonc`. Or add it with the CLI from any directory:

```sh
opencode mcp add docker-gateway --global --url http://127.0.0.1:8811/mcp --header 'Authorization=Bearer {env:MCP_GATEWAY_AUTH_TOKEN}'
```

Then set `"oauth": false` on that server in the config file. The CLI enables OAuth on remote servers by default.

A project config with the same server name **replaces the entire server object**. Repeat every required field in an override.

## 6. What agents can call

The gateway is one MCP endpoint. Behind it:

| Catalog server | Typical tools | Needs |
| --- | --- | --- |
| Postman | `getWorkspaces`, `getCollections`, `runCollection`, … | `postman.postman-api-key` in `.env` |
| DuckDuckGo | `search`, `fetch_content` | none |
| Fetch | `fetch` (URL → markdown) | none |

OpenCode names tools `<server>_<tool>` after normalizing the server name:

```text
docker_gateway_search
docker_gateway_fetch
```

Under default Code Mode they are grouped as `tools.docker_gateway.<tool>(...)`. MCP prompts become slash commands `/<server>:<prompt>`.

Ask OpenCode to search the web, fetch a page, or list Postman workspaces.

---

## Add other MCP servers (OpenCode V2)

Prefer the CLI so unrelated config is preserved. Use `--global` for every project; omit it for the current project only.

### Remote (Streamable HTTP)

```sh
opencode mcp add context7 --url https://mcp.context7.com/mcp
opencode mcp list
```

Remote servers use OAuth unless you turn it off. If `mcp list` shows `needs authentication`, in OpenCode run `/mcps`, select the server, and sign in.

Header credentials (quote `{env:...}` so the shell does not expand it):

```sh
opencode mcp add context7 --url https://mcp.context7.com/mcp --header 'CONTEXT7_API_KEY={env:CONTEXT7_API_KEY}'
```

Equivalent config. Use `oauth: false` only when the server uses an API key or other header, not OAuth:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "context7": {
        "type": "remote",
        "url": "https://mcp.context7.com/mcp",
        "oauth": false,
        "headers": {
          "CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}",
        },
      },
    },
  },
}
```

### Local (stdio)

OpenCode starts the process:

```sh
opencode mcp add everything -- npx -y @modelcontextprotocol/server-everything
```

With env vars:

```sh
opencode mcp add everything --env LOG_LEVEL=info -- npx -y @modelcontextprotocol/server-everything
```

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "everything": {
        "type": "local",
        "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
        "cwd": ".",
        "environment": {
          "LOG_LEVEL": "info",
          "MCP_API_KEY": "{env:MCP_API_KEY}",
        },
      },
    },
  },
}
```

Use `{env:NAME}` in JSON. `$NAME` is not expanded. Disable a server with `"disabled": true` (there is no `enabled` field).

Servers belong under `mcp.servers`, not directly under `mcp`.

### Manage

```sh
opencode mcp list
opencode mcp logout <name>    # drop stored OAuth credentials
```

In OpenCode: `/mcps` to view, connect, disconnect, or authenticate. Disconnecting in `/mcps` does not change config. To remove a server, delete its entry from the config file where you added it.

---

## Pitfalls

| Issue | Fix |
| --- | --- |
| OpenCode tries OAuth against this gateway | Keep `"oauth": false` |
| `{env:MCP_GATEWAY_AUTH_TOKEN}` empty | Export the var in the shell that starts OpenCode; it does not read `.env` |
| `docker-gateway` not connected | Compose down, token mismatch, or port not `127.0.0.1:8811` |
| Duplicate server names | Higher-precedence project config replaces the whole object |
| Secrets in `opencode.jsonc` | Use `{env:NAME}` only |

## Next

- [Step-by-step usage](usage.md) — `.env`, Compose, catalog servers
- [Test with curl / HTTP API](api-testing.md)
- [Test with Postman](postman.md)
