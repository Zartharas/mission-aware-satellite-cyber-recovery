from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = "src.mission_recovery.wp8_observability_evidence"


class ObservabilityOfflinePipelineTests(unittest.TestCase):
    def module(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT)
        return subprocess.run(
            [sys.executable, "-m", MODULE, *args], cwd=ROOT, env=env,
            text=True, capture_output=True, check=True,
        )

    def test_runner_uses_named_observability_cli(self) -> None:
        runner = (ROOT / "scripts" / "run_wp8_observability_binding_preflight.sh").read_text(encoding="utf-8")
        self.assertEqual(runner.count("python3 -m src.mission_recovery.wp8_observability_evidence"), 3)
        self.assertIn("wp8_observability_evidence manifest", runner)
        self.assertIn("wp8_observability_evidence materialize", runner)
        self.assertIn("wp8_observability_evidence validate", runner)
        self.assertNotIn("evidence_paths = [Path(v) for v in sys.argv[3:12]]", runner)

    def test_manifest_through_bound_record_runs_offline(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            ev = temp / "evidence"
            ev.mkdir()
            factor = {
                "run_id": "20260816T000000Z-wp8-observability-offline-fixture",
                "model_version": "0.3.0", "seed": 9301, "mission_state_id": "M2",
                "event_id": "E4", "policy_id": "P7", "contact_condition_id": "C0",
                "evidence_condition_id": "T0", "repo_commit": "0" * 40,
            }
            factor_path = temp / "factor.json"
            factor_path.write_text(json.dumps(factor) + "\n", encoding="utf-8")
            files = {
                "event": ev / "event-instance.json", "policy": ev / "policy-decision.json",
                "event_success": ev / "event-success.json", "post_effect": ev / "post-enforcement-effect.json",
                "p4_probe": ev / "p4-authorized-command-probe.json", "p4_gateway_truth": ev / "p4-command-gateway-truth.jsonl",
                "p4_gateway_decisions": ev / "p4-command-gateway-decisions.jsonl", "truth": ev / "telemetry-truth.jsonl",
                "policy_visible": ev / "policy-visible.jsonl", "health": ev / "observability-health.json",
            }
            files["event"].write_text("{}\n", encoding="utf-8")
            files["policy"].write_text("{}\n", encoding="utf-8")
            files["event_success"].write_text(json.dumps({"event_success": True}) + "\n", encoding="utf-8")
            files["post_effect"].write_text(json.dumps({"containment_observed": False, "required_telemetry_restored": False}) + "\n", encoding="utf-8")
            files["p4_probe"].write_text("{}\n", encoding="utf-8")
            files["p4_gateway_truth"].write_text('{"forwarded": false}\n', encoding="utf-8")
            files["p4_gateway_decisions"].write_text('{"forwarded": false}\n', encoding="utf-8")
            files["truth"].write_text("{}\n", encoding="utf-8")
            files["policy_visible"].write_text("{}\n", encoding="utf-8")
            files["health"].write_text(json.dumps({
                "health_checks_passed": True, "immutable_truth_available": True,
                "policy_visible_plane_available": True, "p4_command_gate_running": True,
            }) + "\n", encoding="utf-8")

            manifest = temp / "manifest.json"
            summary = temp / "summary.json"
            observation = temp / "observation.json"
            record = temp / "run-record.json"
            provenance = temp / "provenance.json"

            t = {
                "run_start": 1_000_000_000, "event": 2_000_000_000,
                "selection": 2_100_000_000, "enforcement": 2_200_000_000,
                "success": 5_200_000_000, "post": 8_200_000_000,
                "health": 8_300_000_000, "manifest": 8_400_000_000,
                "end": 9_000_000_000,
            }

            result = self.module(
                "manifest", "--root", str(temp), "--output", str(manifest),
                "--event-json", str(files["event"]), "--policy-json", str(files["policy"]),
                "--event-success-json", str(files["event_success"]), "--post-effect-json", str(files["post_effect"]),
                "--p4-probe-json", str(files["p4_probe"]), "--p4-gateway-truth", str(files["p4_gateway_truth"]),
                "--p4-gateway-decisions", str(files["p4_gateway_decisions"]), "--truth-jsonl", str(files["truth"]),
                "--policy-visible-jsonl", str(files["policy_visible"]), "--health-json", str(files["health"]),
                "--event-activation-ns", str(t["event"]), "--policy-selection-ns", str(t["selection"]),
                "--policy-enforcement-ns", str(t["enforcement"]), "--event-success-ns", str(t["success"]),
                "--post-effect-ns", str(t["post"]), "--health-ns", str(t["health"]),
                "--manifest-ready-ns", str(t["manifest"]),
            )
            self.assertIn("observability_evidence_manifest=PASS", result.stdout)
            manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(len(manifest_data["source_evidence_sha256"]), 10)
            self.assertIn(str(files["health"].relative_to(temp)), manifest_data["source_evidence_sha256"])

            result = self.module(
                "materialize", "--factor-json", str(factor_path), "--summary-json", str(summary),
                "--observation-json", str(observation), "--run-start-ns", str(t["run_start"]),
                "--event-activation-ns", str(t["event"]), "--event-success-ns", str(t["success"]),
                "--policy-selection-ns", str(t["selection"]), "--policy-enforcement-ns", str(t["enforcement"]),
                "--run-end-ns", str(t["end"]), "--run-start-utc", "2026-08-16T00:00:00Z",
                "--run-end-utc", "2026-08-16T00:00:08Z", "--repo-commit", "0" * 40,
                "--runner-sha", "0" * 64, "--rel", "results/wp8/runtime-binding/observability/" + factor["run_id"],
            )
            self.assertIn("observability_runtime_observation_materialized=PASS", result.stdout)

            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT)
            result = subprocess.run([
                sys.executable, "-m", "src.mission_recovery.wp8_runtime_binding",
                "--observation-json", str(observation),
                "--pilot-config", str(ROOT / "configs" / "wp8_pilot_design.json"),
                "--toolchain-lock", str(ROOT / "configs" / "toolchain-lock.json"),
                "--snapshot-id", "repo-" + ("0" * 40), "--host-architecture", "offline-test",
                "--output-run-json", str(record), "--output-provenance-json", str(provenance),
            ], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
            self.assertIn("WP8_RUNTIME_BINDING_STATUS=PASS", result.stdout)

            result = self.module(
                "validate", "--schema", str(ROOT / "configs" / "experiment_run.schema.json"),
                "--run-record", str(record), "--provenance", str(provenance),
                "--summary", str(summary), "--manifest", str(manifest),
            )
            self.assertIn("schema_valid_observability_bound_run_record=PASS", result.stdout)
            record_data = json.loads(record.read_text(encoding="utf-8"))
            self.assertEqual(record_data["terminal_state"], "RECOVERY_FAILED")
            self.assertEqual(record_data["outcomes"]["mission_objective_completion_ratio"], 0.5)
            self.assertEqual(record_data["outcomes"]["evidence_completeness_ratio"], 2 / 3)
            self.assertIsNone(record_data["timing"]["containment_s"])
            self.assertIsNone(record_data["timing"]["verified_recovery_s"])


if __name__ == "__main__":
    unittest.main()
