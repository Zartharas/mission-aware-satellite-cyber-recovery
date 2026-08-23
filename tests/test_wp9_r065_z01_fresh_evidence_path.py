from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "run_wp9_r065_z01_e1_mechanism.sh"


class WP9R065Z01FreshEvidencePathTests(unittest.TestCase):
    def test_runtime_observation_directory_exists_before_output_path_canonicalization(self):
        source = HARNESS.read_text(encoding="utf-8")
        mkdir_marker = 'mkdir -p "$GROUND" "$OBS"'
        output_check = '$(cd "$(dirname "$OUTPUT_JSON")" && pwd)/$(basename "$OUTPUT_JSON")'

        self.assertIn(mkdir_marker, source)
        self.assertIn(output_check, source)
        self.assertLess(
            source.index(mkdir_marker),
            source.index(output_check),
            "fresh Z01 evidence must create runtime-observation before canonicalizing OUTPUT_JSON",
        )


if __name__ == "__main__":
    unittest.main()
