from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DISPATCHER = ROOT / "scripts" / "run_wp9_r065_bounded_runtime_integration.sh"
HARNESS = ROOT / "scripts" / "run_wp9_r065_z01_e1_mechanism.sh"


class WP9R065Z01FreshEvidencePathTests(unittest.TestCase):
    def test_dispatcher_creates_fresh_runtime_observation_before_execute_z01(self):
        source = DISPATCHER.read_text(encoding="utf-8")
        run_id_marker = 'RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9-r065-z01-s9941-${TOKEN}}"'
        evidence_marker = 'EVIDENCE_DIRECTORY="$ROOT/results/wp9/development/r065/integration/$RUN_ID"'
        mkdir_marker = 'mkdir -p "$EVIDENCE_DIRECTORY/runtime-observation"'
        execute_marker = "execute-z01"

        for marker in (run_id_marker, evidence_marker, mkdir_marker, execute_marker):
            self.assertIn(marker, source)

        self.assertLess(source.index(run_id_marker), source.index(evidence_marker))
        self.assertLess(source.index(evidence_marker), source.index(mkdir_marker))
        self.assertLess(
            source.index(mkdir_marker),
            source.index(execute_marker),
            "fresh Z01 runtime-observation must exist before concrete driver execution",
        )

    def test_harness_keeps_strict_output_path_canonicalization(self):
        source = HARNESS.read_text(encoding="utf-8")
        output_check = '$(cd "$(dirname "$OUTPUT_JSON")" && pwd)/$(basename "$OUTPUT_JSON")'
        self.assertIn(output_check, source)
        self.assertIn(
            '[ERROR] R-065 Z01 output path is not the retained evidence path',
            source,
        )


if __name__ == "__main__":
    unittest.main()
