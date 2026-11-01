"""Contract tests for the Docker MCP Gateway Compose stack."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ComposeContractTests(unittest.TestCase):
    def test_env_example_has_required_secrets(self) -> None:
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("MCP_GATEWAY_AUTH_TOKEN=", text)
        self.assertIn("postman.postman-api-key=", text)

    def test_gitignore_ignores_dotenv(self) -> None:
        lines = [
            line.strip()
            for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        ]
        self.assertIn(".env", lines)

    def test_compose_enables_streaming_catalog_gateway(self) -> None:
        text = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        self.assertIn("--transport=streaming", text)
        self.assertIn("--port=8811", text)
        self.assertIn("--servers=postman,duckduckgo,fetch", text)
        self.assertIn("127.0.0.1:8811:8811", text)
        self.assertIn("/var/run/docker.sock:/var/run/docker.sock", text)
        self.assertIn("MCP_GATEWAY_AUTH_TOKEN: ${MCP_GATEWAY_AUTH_TOKEN:?", text)
        self.assertIn("DOCKER_MCP_IN_CONTAINER", text)
        self.assertIn("--secrets=/run/secrets/mcp_secrets", text)
        self.assertIn("file: .env", text)
        self.assertNotIn("--allow-unauthenticated", text)
        self.assertNotIn("0.0.0.0", text)

    def test_readme_keeps_remote_oauth_disabled(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("oauth: false", text)
        self.assertIn("docs/usage.md", text)
        self.assertIn("docs/api-testing.md", text)
        self.assertIn("docs/postman.md", text)

    def test_usage_doc_covers_compose_and_opencode(self) -> None:
        text = (ROOT / "docs/usage.md").read_text(encoding="utf-8")
        self.assertIn("docker compose up -d", text)
        self.assertIn("export MCP_GATEWAY_AUTH_TOKEN", text)
        self.assertIn("opencode mcp list", text)
        self.assertIn("postman.postman-api-key", text)

    def test_api_testing_doc_covers_mcp_jsonrpc(self) -> None:
        text = (ROOT / "docs/api-testing.md").read_text(encoding="utf-8")
        self.assertIn("/health", text)
        self.assertIn("Mcp-Session-Id", text)
        self.assertIn("tools/list", text)
        self.assertIn("tools/call", text)
        self.assertIn("Authorization: Bearer", text)

    def test_postman_collection_can_be_imported(self) -> None:
        text = (ROOT / "docs/postman.md").read_text(encoding="utf-8")
        self.assertIn("mcp-gateway.postman_collection.json", text)
        self.assertIn("oauth: false", text)
        collection = (ROOT / "docs/postman/mcp-gateway.postman_collection.json").read_text(
            encoding="utf-8"
        )
        self.assertIn("http://127.0.0.1:8811", collection)
        self.assertIn("/mcp", collection)
        self.assertIn("Mcp-Session-Id", collection)
        self.assertIn("tools/list", collection)

    def test_opencode_config_uses_remote_bearer(self) -> None:
        text = (ROOT / "opencode.jsonc").read_text(encoding="utf-8")
        self.assertIn('"type": "remote"', text)
        self.assertIn("http://127.0.0.1:8811/mcp", text)
        self.assertIn('"oauth": false', text)
        self.assertIn("Authorization", text)
        self.assertIn("Bearer {env:MCP_GATEWAY_AUTH_TOKEN}", text)


if __name__ == "__main__":
    unittest.main()
