#!/usr/bin/env bash
# OpenCode stdio entry for the standalone Postman MCP server.
# Reads the key from the repo .env so OpenCode's background service does not
# need POSTMAN_API_KEY in its own environment.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${POSTMAN_MCP_IMAGE:-mcp/postman}"

api_key="${POSTMAN_API_KEY:-}"
if [[ -z "$api_key" && -f "$ROOT/.env" ]]; then
  api_key="$(sed -n 's/^postman\.postman-api-key=//p' "$ROOT/.env" | head -n 1 | tr -d '\r')"
  api_key="${api_key%\"}"
  api_key="${api_key#\"}"
  api_key="${api_key%\'}"
  api_key="${api_key#\'}"
fi

if [[ -z "$api_key" ]]; then
  printf 'error: POSTMAN_API_KEY is not set and postman.postman-api-key is missing from %s/.env\n' "$ROOT" >&2
  exit 1
fi

if (($# == 0)); then
  set -- --full
fi

export POSTMAN_API_KEY="$api_key"
exec docker run -i --rm -e POSTMAN_API_KEY "$IMAGE" "$@"
