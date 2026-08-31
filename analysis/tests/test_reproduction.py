import json
import shutil
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
            self.assertEqual(
                record["validation"][
                    "C2_model_contrast_interval_regression"
                ],
                "PASS",
            )
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

    def test_reference_manifest_rejects_tampered_expected_output(self):
        analysis = Path(__file__).resolve().parents[1]
        script = analysis / "reproduce_wp10.py"
        source_reference = analysis / "reference"

        with tempfile.TemporaryDirectory() as tmp:
            reference = Path(tmp) / "reference"

            shutil.copytree(
                source_reference,
                reference,
            )

            target = (
                reference /
                "expected" /
                "29-wp10c2-m07-model-contrasts.tsv"
            )

            target.write_text(
                target.read_text(
                    encoding="utf-8"
                ) + "\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--reference-dir",
                    str(reference),
                    "--validate",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertNotEqual(
                proc.returncode,
                0,
            )

            self.assertIn(
                "reference SHA-256 mismatch",
                proc.stdout +
                "\n" +
                proc.stderr,
            )


if __name__ == "__main__":
    unittest.main()
