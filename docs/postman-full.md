# Run the standalone Postman MCP server (full)

The gateway already exposes Postman through the Docker catalog. This optional setup runs the official `mcp/postman` image directly with the **full** toolset, which adds the 100+ tools that the default catalog integration may not expose.

The standalone server uses **stdio**, not HTTP. It has no port and no health endpoint. OpenCode launches it as a child process over stdio.

## Before you begin

- Docker Engine with the daemon running
- A Postman API key stored as `postman.postman-api-key` in `.env`

## 1. Verify the server

From the repo root:

```bash
scripts/setup-postman-mcp.sh
```

The script:

1. Reads `POSTMAN_API_KEY` from the environment, or `postman.postman-api-key` from `.env`.
2. Pulls `mcp/postman`.
3. Starts the image with `--full` and sends an MCP `initialize` request over stdio.
4. Exits non-zero if the handshake fails.

Useful options:

```bash
scripts/setup-postman-mcp.sh --print-opencode   # print the OpenCode block only
scripts/setup-postman-mcp.sh --no-pull          # skip docker pull
scripts/setup-postman-mcp.sh --minimal          # verify another toolset
scripts/setup-postman-mcp.sh --code
scripts/setup-postman-mcp.sh --learn
scripts/setup-postman-mcp.sh --context-graph
```

`--full` is the default. `POSTMAN_MCP_MODE` is **not** a supported variable; mode is selected by the CLI flag.

## 2. How the key reaches OpenCode

OpenCode does **not** read Compose `.env`. The `postman-full` entry therefore runs a small wrapper:

```text
scripts/run-postman-mcp-full.sh
```

The wrapper reads:

1. `POSTMAN_API_KEY` from its environment, if set.
2. Otherwise `postman.postman-api-key` from the repo `.env`.

It then starts `docker run -i --rm -e POSTMAN_API_KEY mcp/postman --full`. The key is passed through the environment, not on the container command line. `.env` is gitignored, and the key never appears in `opencode.jsonc`.

No export or OpenCode service restart is required. To rotate the key, update `.env`; the next session picks it up.

## 3. OpenCode config

This repo's `opencode.jsonc` already defines the server:

```jsonc
"postman-full": {
  "type": "local",
  "command": ["bash", "scripts/run-postman-mcp-full.sh", "--full"]
}
```

The server coexists with `docker-gateway`. Because the names differ, tools are distinct:

| Server | Tool prefix |
| --- | --- |
| `docker-gateway` | `docker_gateway_*` |
| `postman-full` | `postman_full_*` |

Both expose Postman tools, so expect some duplication. If you only want the standalone full server, remove `postman` from `--servers=` in `compose.yaml` and recreate the gateway:

```bash
docker compose up -d --force-recreate
```

## 4. Test it

### Handshake

```bash
scripts/setup-postman-mcp.sh
```

Expect:

```text
OK: Postman MCP --full responded (server 2.11.0).
```

The server version can differ after an image update.

### Call a tool over stdio

This sends `initialize`, `notifications/initialized`, and `tools/call` to the same wrapper OpenCode uses:

```bash
{
  printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"docs-test","version":"0"}}}'
  printf '%s\n' '{"jsonrpc":"2.0","method":"notifications/initialized"}'
  printf '%s\n' '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"getAuthenticatedUser","arguments":{}}}'
} | scripts/run-postman-mcp-full.sh
```

Expect two JSON-RPC responses. The second has `"id":2` and a `"result"` containing your Postman user. This proves the API key works, not just that the container starts.

### OpenCode

```bash
opencode mcp list
```

You want:

```text
postman-full  connected
```

OpenCode reloads configuration automatically, so a running session does not need a restart after the config change.

### Agent call

Ask OpenCode:

> List my Postman workspaces.

A successful call returns workspace names through `postman_full_*` tools.

## 5. Tool names

Full tools appear as `postman_full_<tool>`, for example `postman_full_getWorkspaces` and `postman_full_runCollection`. Use `postman_full_*` when you need a tool that only exists in the full set.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `postman-full  failed` | Run `scripts/setup-postman-mcp.sh` to see the handshake error |
| `POSTMAN_API_KEY is not set and postman.postman-api-key is missing` | Add the key to `postman.postman-api-key` in `.env`; the wrapper reads it on the next connection |
| `the Docker daemon is not reachable` | Start Docker: `sudo systemctl start docker` |
| `401` or auth errors from Postman | Regenerate the API key and update `.env` |
| Script hangs | Check `docker ps` for a stuck container; the MCP server exits when stdin closes |
| Duplicate Postman tools | Expected with coexisting servers; use `postman_full_*` or remove Postman from the gateway |

See also [Set up OpenCode](opencode.md) and [Test the gateway in the Postman app](postman.md).
