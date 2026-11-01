# MCP Gateway Compose Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Docker Compose MCP Gateway that OpenCode can call over Streamable HTTP for Postman, DuckDuckGo search, and Fetch.

**Architecture:** One `docker/mcp-gateway` service publishes `127.0.0.1:8811`, starts catalog servers via the Docker socket, and authenticates with a Bearer token from `.env`. OpenCode connects as a remote MCP client to `/mcp`.

**Tech Stack:** Docker Compose, `docker/mcp-gateway`, Docker MCP Catalog (`postman`, `duckduckgo`, `fetch`), OpenCode V2 remote MCP.

**Spec:** Conversation design 2026-11-01 — gateway for catalog tools; v1 servers postman, duckduckgo, fetch; no Crawl4AI; secrets in `.env` not git.

## Global Constraints

- Bind the published port to `127.0.0.1` only.
- Streamable HTTP on port `8811`, endpoint `/mcp`.
- Do not commit `.env` or API keys.
- Do not use `--allow-unauthenticated`.
- Catalog server names: `postman`, `duckduckgo`, `fetch`.
- Postman secret key name: `postman.postman-api-key`.
- Gateway auth: `MCP_GATEWAY_AUTH_TOKEN` as `Authorization: Bearer …`.
- Linux Docker Engine: set `DOCKER_MCP_IN_CONTAINER=1`.

## Review Focus

- Missing `.env` makes `docker compose up` fail with a clear secrets-file error, not a silent empty gateway.
- OpenCode without the Bearer header gets 401 from `/mcp`.
- `/health` stays reachable without auth.
- Publishing on `0.0.0.0` would expose tools on the LAN — compose must use `127.0.0.1`.
- Extra keys in the secrets file must not be committed; `.gitignore` must list `.env`.

## File structure

- Create: `tests/test_compose_contract.py` — contract tests for compose, env example, gitignore, OpenCode config
- Create: `compose.yaml` — gateway service
- Create: `.env.example` — required keys
- Create: `.gitignore`
- Create: `opencode.jsonc` — project-local OpenCode remote MCP
- Create: `README.md`

---

### Task 1: Compose contract tests

**Files:**
- Create: `tests/test_compose_contract.py`

**Interfaces:**
- Consumes: nothing
- Produces: unittest module `tests.test_compose_contract` with four tests named below

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_compose_contract.py
# test_env_example_has_required_secrets
#   asserts .env.example contains MCP_GATEWAY_AUTH_TOKEN= and postman.postman-api-key=
# test_gitignore_ignores_dotenv
#   asserts a .gitignore line that is exactly .env
# test_compose_enables_streaming_catalog_gateway
#   asserts compose.yaml contains:
#     --transport=streaming
#     --port=8811
#     --servers=postman,duckduckgo,fetch
#     127.0.0.1:8811:8811
#     /var/run/docker.sock:/var/run/docker.sock
#     MCP_GATEWAY_AUTH_TOKEN
#     DOCKER_MCP_IN_CONTAINER
#     --secrets=/run/secrets/mcp_secrets
# test_opencode_config_uses_remote_bearer
#   asserts opencode.jsonc contains type remote, http://127.0.0.1:8811/mcp, oauth false,
#   and Authorization Bearer {env:MCP_GATEWAY_AUTH_TOKEN}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_compose_contract -v`

Expected: FAIL because the files do not exist (FileNotFoundError) or required strings are missing.

- [ ] **Step 3: Add compose.yaml, .env.example, .gitignore, opencode.jsonc**

Gateway command: `--transport=streaming --port=8811 --servers=postman,duckduckgo,fetch --secrets=/run/secrets/mcp_secrets`. Publish `127.0.0.1:8811:8811`. Mount docker.sock. Compose secret `mcp_secrets` from `.env`. Healthcheck `wget -O- http://127.0.0.1:8811/health`. `pull_policy: always`. `restart: unless-stopped`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_compose_contract -v`

Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add tests/test_compose_contract.py compose.yaml .env.example .gitignore opencode.jsonc
git commit -m "feat: add Docker MCP Gateway compose stack for OpenCode"
```

### Task 2: README and compose config verification

**Files:**
- Create: `README.md`
- Test: `tests/test_compose_contract.py` (add `test_readme_documents_up_and_opencode` if needed — fold into README content check in this task via compose config command instead)

**Interfaces:**
- Consumes: compose.yaml from Task 1
- Produces: README with copy-.env, compose up, OpenCode header, how to add a catalog server

- [ ] **Step 1: Write README covering setup, secrets, OpenCode, adding servers**

Must include: `cp .env.example .env`, `docker compose up -d`, `http://127.0.0.1:8811/mcp`, Bearer token, Postman API key, adding `--servers=` names.

- [ ] **Step 2: Run `docker compose config`**

Run: `docker compose config`

Expected: exit 0 after a temporary `.env` exists for the secrets file (create from example in the test command if needed, do not commit `.env`).

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: explain MCP Gateway compose setup for OpenCode"
```
