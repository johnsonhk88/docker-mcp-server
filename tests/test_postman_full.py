"""Contract tests for the standalone Postman MCP full server setup."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PostmanFullContractTests(unittest.TestCase):
    def test_setup_script_is_executable(self) -> None:
        script = ROOT / "scripts" / "setup-postman-mcp.sh"
        self.assertTrue(script.is_file(), f"missing {script}")
        self.assertTrue(os.access(script, os.X_OK), f"{script} is not executable")

    def test_setup_script_uses_full_mode_and_api_key(self) -> None:
        text = (ROOT / "scripts" / "setup-postman-mcp.sh").read_text(encoding="utf-8")
        self.assertIn("mcp/postman", text)
        self.assertIn("--full", text)
        self.assertIn("POSTMAN_API_KEY", text)
        self.assertIn(r"postman\.postman-api-key=", text)
        self.assertIn("docker run", text)
        self.assertNotIn("POSTMAN_MCP_MODE", text)

    def test_runner_script_reads_dotenv_and_execs_full_server(self) -> None:
        script = ROOT / "scripts" / "run-postman-mcp-full.sh"
        self.assertTrue(script.is_file(), f"missing {script}")
        self.assertTrue(os.access(script, os.X_OK), f"{script} is not executable")
        text = script.read_text(encoding="utf-8")
        self.assertIn(r"postman\.postman-api-key=", text)
        self.assertIn("mcp/postman", text)
        self.assertIn("--full", text)
        self.assertIn("exec docker run", text)
        self.assertIn('"$@"', text)
        self.assertNotIn("POSTMAN_MCP_MODE", text)

    def test_opencode_config_adds_postman_full_local_server(self) -> None:
        text = (ROOT / "opencode.jsonc").read_text(encoding="utf-8")
        self.assertIn('"postman-full"', text)
        self.assertIn('"type": "local"', text)
        self.assertIn('"scripts/run-postman-mcp-full.sh"', text)

    def test_docs_cover_postman_full_setup(self) -> None:
        text = (ROOT / "docs" / "postman-full.md").read_text(encoding="utf-8")
        self.assertIn("scripts/setup-postman-mcp.sh", text)
        self.assertIn("scripts/run-postman-mcp-full.sh", text)
        self.assertIn("POSTMAN_API_KEY", text)
        self.assertIn("postman-full", text)
        self.assertIn("opencode mcp list", text)

    def test_readme_documents_standalone_setup_and_test(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Standalone Postman full server (optional)", text)
        self.assertIn("## Test", text)
        self.assertIn("scripts/setup-postman-mcp.sh", text)
        self.assertIn("postman_full_*", text)
        self.assertIn("docs/postman-full.md", text)
        self.assertIn("opencode mcp list", text)

    def test_usage_and_opencode_link_standalone_server(self) -> None:
        usage = (ROOT / "docs" / "usage.md").read_text(encoding="utf-8")
        self.assertIn("## 6. Optional: standalone Postman full server", usage)
        self.assertIn("scripts/setup-postman-mcp.sh", usage)
        self.assertIn("postman_full_*", usage)
        self.assertIn("postman-full.md", usage)

        opencode = (ROOT / "docs" / "opencode.md").read_text(encoding="utf-8")
        self.assertIn("### Standalone Postman full server", opencode)
        self.assertIn("scripts/run-postman-mcp-full.sh", opencode)
        self.assertIn("postman_full_*", opencode)
        self.assertIn("postman-full.md", opencode)

    def test_postman_app_doc_distinguishes_standalone_server(self) -> None:
        text = (ROOT / "docs" / "postman.md").read_text(encoding="utf-8")
        self.assertIn("# Test the MCP Gateway in the Postman app", text)
        self.assertIn("standalone", text)
        self.assertIn("postman-full.md", text)

    def test_postman_full_doc_covers_tool_call_test(self) -> None:
        text = (ROOT / "docs" / "postman-full.md").read_text(encoding="utf-8")
        self.assertIn("## 4. Test it", text)
        self.assertIn("getAuthenticatedUser", text)
        self.assertIn("notifications/initialized", text)
        self.assertIn("scripts/run-postman-mcp-full.sh", text)


if __name__ == "__main__":
    unittest.main()
