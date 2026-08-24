from __future__ import annotations

import re
import stat
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_wp9_r069_campaign_one_position.sh"


class R069EntrypointTests(unittest.TestCase):
    def test_entrypoint_is_executable_and_single_invocation(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        mode = SCRIPT.stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR)
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertEqual(text.count("execute-request"), 1)
        self.assertEqual(text.count("prepare-next"), 1)
        self.assertEqual(text.count("append-result"), 1)
        self.assertIsNone(re.search(r"(?m)^\s*git\s+pull\b", text))
        self.assertNotIn("for POSITION", text)
        self.assertNotIn("for position", text)
        self.assertNotIn("while true", text)
        self.assertNotIn("automatic_retry_performed=true", text)
        self.assertNotIn("automatic_next_case_performed=true", text)

    def test_entrypoint_derives_metadata_from_operator_summary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('SUMMARY="$TMP/prepared/request-summary.json"', text)
        self.assertIn('"RUNTIME_FAMILY": summary["runtime_family"]', text)
        self.assertIn('"RUNTIME_VARIANT": summary["runtime_variant"]', text)
        self.assertNotIn('request["runtime_family"]', text)
        self.assertNotIn('request["runtime_variant"]', text)

    def test_retry_label_is_derived_only_from_retained_invalid_state(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('history[-1].get("attempt_status") == "INVALID"', text)
        self.assertIn('retry = "-retry" if is_retry else ""', text)
        self.assertIn('--run-id "$RUN_ID_OVERRIDE"', text)

    def test_atomic_operator_lock_precedes_position_derivation_and_execution(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('LOCK_DIR="/tmp/wp9-r069-campaign-one-position.lock"', text)
        self.assertIn('mkdir "$LOCK_DIR"', text)
        self.assertIn('rmdir "$LOCK_DIR"', text)
        lock_index = text.index('mkdir "$LOCK_DIR"')
        prepare_index = text.index("prepare-next")
        execute_index = text.index("execute-request")
        self.assertLess(lock_index, prepare_index)
        self.assertLess(prepare_index, execute_index)

    def test_nonzero_executor_path_does_not_append_history(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        nonzero = text.split('if [[ "$RC" -ne 0 ]]', 1)[1].split(
            '[[ -f "$EXEC_OUT" ]]', 1
        )[0]
        self.assertIn("attempt_history_append_performed=false", nonzero)
        self.assertNotIn("append-result", nonzero)
        self.assertIn("runtime_safety_audit", nonzero)
        self.assertIn("STOP HERE", nonzero)

    def test_append_failure_runs_safety_audit_before_stopping(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("attempt_history_append=FAIL", text)
        append_failure = text.split("attempt_history_append=FAIL", 1)[1]
        self.assertIn("runtime_safety_audit", append_failure)
        self.assertIn("STOP HERE", append_failure)


if __name__ == "__main__":
    unittest.main()
