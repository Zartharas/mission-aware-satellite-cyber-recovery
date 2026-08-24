from __future__ import annotations

import os
import stat
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_wp9_r066_final_campaign_trial.sh"


class WP9R066CampaignEntrypointTests(unittest.TestCase):
    def test_entrypoint_is_executable_and_single_trial_only(self) -> None:
        mode = SCRIPT.stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR)

        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("validate-static", text)
        self.assertIn("authorization-request", text)
        self.assertIn("build-request", text)
        self.assertIn("execute-request", text)
        self.assertIn(
            "src.mission_recovery.wp9_r066_campaign_runtime_executor",
            text,
        )

        execute_block = text.split("  execute-request)", 1)[1].split("  *)", 1)[0]
        self.assertNotIn("for ", execute_block)
        self.assertNotIn("while ", execute_block)
        self.assertNotIn("docker run", execute_block)
        self.assertNotIn("docker compose", execute_block)
        self.assertNotIn("automatic retry", execute_block.lower())
        self.assertIn("No loop, retry, or next-case path exists", execute_block)

    def test_entrypoint_does_not_embed_campaign_authorization(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("WP9_R066_FINAL_CAMPAIGN_RUNTIME_AUTHORIZED=1", text)
        self.assertNotIn("WP9_R066_AUTHORIZED_RUN_ID=", text)
        self.assertNotIn("WP9_R066_AUTHORIZED_SEED=", text)
        self.assertNotIn("WP9_R066_AUTHORIZED_CELL=", text)
        self.assertNotIn("WP9_R066_AUTHORIZED_REPO_SHA=", text)

    def test_legacy_r064_entrypoint_remains_fail_closed(self) -> None:
        legacy = (
            ROOT / "scripts" / "run_wp9_r064_final_campaign_trial.sh"
        ).read_text(encoding="utf-8")
        block = legacy.split("  execute-trial)", 1)[1].split("  *)", 1)[0]
        self.assertIn("execution remains blocked", block)
        self.assertIn("exit 3", block)
        self.assertNotIn("docker run", block)


if __name__ == "__main__":
    unittest.main()
