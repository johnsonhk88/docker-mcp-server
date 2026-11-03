#!/usr/bin/env bash
# Verify the standalone Postman MCP server used by the "postman-full" OpenCode entry.
# The server speaks MCP over stdio; OpenCode starts it. This script only prepares
# and verifies the image, then prints the client-side steps.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${POSTMAN_MCP_IMAGE:-mcp/postman}"
MODE="--full"
DO_PULL=1
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage: scripts/setup-postman-mcp.sh [options]

Verify the standalone Postman MCP server over stdio and show the OpenCode steps.

Options:
  --full | --minimal | --code | --learn | --context-graph
      Toolset to verify. Default: --full.
  --no-pull
      Do not pull the image before verifying.
  --print-opencode
      Print the OpenCode config block and exit without contacting Docker.
  -h, --help
      Show this help.

API key lookup order:
  1. POSTMAN_API_KEY in the environment
  2. postman.postman-api-key in the repo .env

The server is stdio-only. It has no HTTP port; OpenCode launches it per session.
EOF
}

print_opencode() {
  cat <<EOF
{
  "postman-full": {
    "type": "local",
    "command": ["bash", "scripts/run-postman-mcp-full.sh", "$MODE"]
  }
}
EOF
}

while (($# > 0)); do
  case "$1" in
    --full | --minimal | --code | --learn | --context-graph)
      MODE="$1"
      ;;
    --no-pull)
      DO_PULL=0
      ;;
    --print-opencode)
      PRINT_ONLY=1
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      printf 'error: unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [[ "$PRINT_ONLY" -eq 1 ]]; then
  print_opencode
  exit 0
fi

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

command -v docker >/dev/null 2>&1 || die "docker is not installed"
docker info >/dev/null 2>&1 || die "the Docker daemon is not reachable"

api_key="${POSTMAN_API_KEY:-}"
if [[ -z "$api_key" && -f "$ROOT/.env" ]]; then
  api_key="$(sed -n 's/^postman\.postman-api-key=//p' "$ROOT/.env" | head -n 1 | tr -d '\r')"
  api_key="${api_key%\"}"
  api_key="${api_key#\"}"
  api_key="${api_key%\'}"
  api_key="${api_key#\'}"
fi
[[ -n "$api_key" ]] || die "set POSTMAN_API_KEY or postman.postman-api-key in $ROOT/.env"

if [[ "$DO_PULL" -eq 1 ]]; then
  printf 'Pulling %s ...\n' "$IMAGE"
  docker pull "$IMAGE" >/dev/null
fi

printf 'Verifying %s %s over stdio ...\n' "$IMAGE" "$MODE"

request='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"setup-postman-mcp","version":"1"}}}'
out="$(mktemp)"
err="$(mktemp)"
trap 'rm -f "$out" "$err"' EXIT

# Let docker copy the key from this process environment with -e POSTMAN_API_KEY,
# keeping it out of the container command line.
export POSTMAN_API_KEY="$api_key"

run=(docker run -i --rm -e POSTMAN_API_KEY "$IMAGE" "$MODE")
if command -v timeout >/dev/null 2>&1; then
  run=(timeout 90 "${run[@]}")
fi

if ! printf '%s\n' "$request" | "${run[@]}" >"$out" 2>"$err"; then
  printf 'error: the Postman MCP server did not start cleanly.\n' >&2
  tail -n 20 "$err" >&2 || true
  exit 1
fi

if ! grep -q '"serverInfo"' "$out"; then
  printf 'error: no MCP initialize response was returned.\n' >&2
  tail -n 20 "$err" >&2 || true
  exit 1
fi

version="$(sed -n 's/.*"version":"\([^"]*\)".*/\1/p' "$out" | head -n 1)"
printf 'OK: Postman MCP %s responded (server %s).\n' "$MODE" "${version:-unknown}"

cat <<'EOF'

Next:
  opencode mcp list

The repo's opencode.jsonc defines this server as "postman-full". OpenCode runs
scripts/run-postman-mcp-full.sh, which reads the key from .env at startup, so
no export or service restart is needed.
EOF
