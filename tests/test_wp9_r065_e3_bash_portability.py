from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "run_wp9_r065_e3_mechanism.sh"


class WP9R065E3BashPortabilityTests(unittest.TestCase):
    def test_result_path_uses_explicit_portable_lowercase_case_id(self):
        source = HARNESS.read_text(encoding="utf-8")
        self.assertIn(
            'CASE_SAFE="$(printf \'%s\' "$CASE_ID" | tr \'[:upper:]\' \'[:lower:]\')"',
            source,
        )
        self.assertIn('EXPECTED_OUTPUT="$OBS/${CASE_SAFE}-driver-result.json"', source)
        self.assertNotIn("${CASE_ID:l}", source)


if __name__ == "__main__":
    unittest.main()
