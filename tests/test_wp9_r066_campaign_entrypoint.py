from __future__ import annotations

import contextlib
import io
import stat
import unittest
from pathlib import Path
from unittest.mock import patch

from src.mission_recovery import wp9_r066_campaign_runtime_executor as executor_cli
from src.mission_recovery import wp9_r066_final_campaign_runtime_binding as binding_cli

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_wp9_r066_final_campaign_trial.sh"


def _outer_command_block(text: str, command: str) -> str:
    start = f"\n  {command})\n"
    end = "\n  *)\n"
    if start not in text or end not in text:
        raise AssertionError(f"outer shell command markers missing: {command}")
    return text.split(start, 1)[1].rsplit(end, 1)[0]


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
        self.assertIn(
            "src.mission_recovery.wp9_r066_campaign_evidence_freshness",
            text,
        )

        execute_block = _outer_command_block(text, "execute-request")
        self.assertNotIn("for ", execute_block)
        self.assertNotIn("docker run", execute_block)
        self.assertNotIn("docker compose", execute_block)
        self.assertNotIn("run_source_harness", execute_block)
        self.assertEqual(
            execute_block.count(
                "src.mission_recovery.wp9_r066_campaign_runtime_executor"
            ),
            1,
        )
        self.assertEqual(execute_block.count("execute-request"), 1)
        self.assertLess(
            execute_block.index(
                "src.mission_recovery.wp9_r066_campaign_evidence_freshness"
            ),
            execute_block.index(
                "src.mission_recovery.wp9_r066_campaign_runtime_executor"
            ),
        )
        self.assertIn("No retry or next-case", execute_block)

    def test_entrypoint_argument_loop_does_not_execute_trials(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        execute_block = _outer_command_block(text, "execute-request")
        self.assertIn('while [[ "$#" -gt 0 ]]', execute_block)
        loop_body = execute_block.split('while [[ "$#" -gt 0 ]]', 1)[1].split(
            "    done", 1
        )[0]
        self.assertNotIn("python3 -m", loop_body)
        self.assertNotIn("docker", loop_body)
        self.assertNotIn("execute-request", loop_body)

    def test_direct_hardened_executor_runs_freshness_before_runtime_binding(self) -> None:
        calls: list[str] = []
        request = {"run_id": "r066-direct-freshness"}

        def freshness(_: dict) -> dict:
            calls.append("freshness")
            return {"evidence_directory_fresh": True}

        def execute(**_: object) -> dict:
            calls.append("execute")
            return {"attempt_status": "VALID"}

        with patch.object(
            executor_cli,
            "validate_fresh_campaign_evidence",
            side_effect=freshness,
        ), patch.object(
            executor_cli.binding,
            "execute_campaign_runtime_request",
            side_effect=execute,
        ):
            result = executor_cli.execute_request(request)

        self.assertEqual(calls, ["freshness", "execute"])
        self.assertEqual(result["attempt_status"], "VALID")

    def test_direct_hardened_executor_stops_when_freshness_fails(self) -> None:
        request = {"run_id": "r066-direct-stale"}
        with patch.object(
            executor_cli,
            "validate_fresh_campaign_evidence",
            side_effect=ValueError("stale evidence"),
        ), patch.object(
            executor_cli.binding,
            "execute_campaign_runtime_request",
        ) as execute:
            with self.assertRaisesRegex(ValueError, "stale evidence"):
                executor_cli.execute_request(request)
            execute.assert_not_called()

    def test_unhardened_binding_cli_exposes_no_execution_command(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as blocked:
                binding_cli.main(["execute-request"])
        self.assertEqual(blocked.exception.code, 2)

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
        block = _outer_command_block(legacy, "execute-trial")
        self.assertIn("execution remains blocked", block)
        self.assertIn("exit 3", block)
        self.assertNotIn("docker run", block)


if __name__ == "__main__":
    unittest.main()
