import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class WP10ReproductionTest(unittest.TestCase):
    def test_full_reference_regression(self):
        analysis = Path(__file__).resolve().parents[1]
        script = analysis / "reproduce_wp10.py"
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(script), "--validate", "--output-dir", tmp],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            record = json.loads((Path(tmp) / "reproduction-validation.json").read_text())
            self.assertEqual(record["validation"]["overall"], "PASS")
            self.assertEqual(record["provenance"]["valid_runs"], 720)
            self.assertFalse(record["provenance"]["original_analysis_source_preserved"])
            self.assertFalse(record["provenance"]["p_values_computed"])
            self.assertFalse(record["provenance"]["weighted_score_computed"])
            self.assertFalse(record["provenance"]["global_policy_ranking_computed"])
            self.assertFalse(record["provenance"]["simultaneous_pareto_confidence_claim"])
            self.assertEqual(record["c1"]["m03_one_sided95_upper"], 0.09503385285530419)
            self.assertEqual(
                record["validation"]["P5_original_bootstrap_endpoint_exact_replay"],
                "NOT_CLAIMED_OR_REQUIRED_SEED_NOT_PRESERVED",
            )


if __name__ == "__main__":
    unittest.main()
