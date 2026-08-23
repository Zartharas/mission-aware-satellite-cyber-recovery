from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_wp9_r061_e1_route_validation.sh"


class WP9R061E1RuntimeHarnessTests(unittest.TestCase):
    def _blocked_run(self, case_id: str, **updates: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        for key in (
            "WP9_R061_DEVELOPMENT_RUNTIME_AUTHORIZED",
            "WP9_R061_AUTHORIZED_CASE",
            "WP9_R061_AUTHORIZED_REPO_SHA",
        ):
            env.pop(key, None)
        env.update(updates)
        return subprocess.run(
            ["/bin/bash", str(RUNNER), case_id],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_runner_is_bash32_safe_and_single_case_only(self) -> None:
        completed = subprocess.run(
            ["/bin/bash", "-n", str(RUNNER)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('[[ "$#" -eq 1 ]]', text)
        self.assertNotIn("mapfile", text)
        self.assertNotIn("readarray", text)
        self.assertNotIn("declare -A", text)
        self.assertNotIn("results/wp9/campaign", text)
        self.assertIn("automatic_retry_allowed=false", text)
        self.assertIn("automatic_next_case_allowed=false", text)

    def test_runner_freezes_exact_five_case_mapping(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        expected = (
            'X01) CELL_ID="A05"; SEED="9921" ;;',
            'X02) CELL_ID="A08"; SEED="9922" ;;',
            'X03) CELL_ID="A02"; SEED="9923" ;;',
            'X04) CELL_ID="A06"; SEED="9924" ;;',
            'X05) CELL_ID="A09"; SEED="9925" ;;',
        )
        for row in expected:
            self.assertIn(row, text)
        self.assertIn("results/wp9/development/r061/e1", text)

    def test_runtime_is_blocked_by_default_before_docker_or_evidence(self) -> None:
        completed = self._blocked_run("X01")
        combined = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 3, combined)
        self.assertIn("development runtime remains blocked", combined)

        text = RUNNER.read_text(encoding="utf-8")
        gate = text.index('[[ "$RUNTIME_AUTHORIZED" == "1" ]]')
        docker = text.index("docker info")
        evidence = text.index('mkdir -p "$GROUND" "$OBS"')
        self.assertLess(gate, docker)
        self.assertLess(gate, evidence)

    def test_authorization_is_case_scoped(self) -> None:
        completed = self._blocked_run(
            "X01",
            WP9_R061_DEVELOPMENT_RUNTIME_AUTHORIZED="1",
            WP9_R061_AUTHORIZED_CASE="X02",
            WP9_R061_AUTHORIZED_REPO_SHA="0" * 40,
        )
        combined = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 3, combined)
        self.assertIn("authorization is not for requested case X01", combined)

    def test_authorization_is_exact_repo_sha_scoped(self) -> None:
        completed = self._blocked_run(
            "X01",
            WP9_R061_DEVELOPMENT_RUNTIME_AUTHORIZED="1",
            WP9_R061_AUTHORIZED_CASE="X01",
            WP9_R061_AUTHORIZED_REPO_SHA="0" * 40,
        )
        combined = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 3, combined)
        self.assertIn("authorization SHA does not match", combined)

    def test_runner_preserves_e1_temporal_and_measurement_contract(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        activation = text.index('PHASE="EVENT_ACTIVATION"')
        selection = text.index('PHASE="POLICY_SELECTION"')
        enforcement = text.index('PHASE="POLICY_ENFORCEMENT"')
        confirmation = text.index('PHASE="EVENT_SUCCESS_CONFIRMATION"')
        self.assertLess(activation, selection)
        self.assertLess(selection, enforcement)
        self.assertLess(enforcement, confirmation)
        self.assertIn("policy_selection_not_gated_on_event_success=true", text)
        self.assertIn("matched_attacker_reset_probe_count=2", text)
        self.assertIn("post_response_authorized_noop_attempted=1", text)
        self.assertIn("gateway_decision_count=3", text)
        self.assertIn("finalize-development", text)

    def test_runner_uses_frozen_horizon_not_wall_clock_duration(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("NOMINAL_DURATION_SECONDS=90", text)
        self.assertIn(
            "ANALYSIS_END_NS=$((EVENT_ACTIVATION_NS + 30 * 1000000000))",
            text,
        )
        self.assertIn("post_event_analysis_horizon_s=30", text)
        self.assertIn("runner_duration_used_as_metric_input=false", text)
        self.assertIn("runtime_health_passed=true", text)

    def test_runner_releases_gateway_then_audits_residue(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        auxiliary = text.index('PHASE="AUXILIARY_CLEANUP"')
        nominal = text.index('PHASE="NOMINAL_RUNTIME_COMPLETION"')
        audit = text.index('PHASE="CLEANUP_AUDIT"')
        self.assertLess(auxiliary, nominal)
        self.assertLess(nominal, audit)
        self.assertIn('docker rm -f "$GATEWAY"', text[auxiliary:nominal])
        self.assertIn('docker network rm "$NETWORK"', text[audit:])
        self.assertIn("residual_runtime=none", text[audit:])


if __name__ == "__main__":
    unittest.main()
