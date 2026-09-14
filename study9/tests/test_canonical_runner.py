from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from study9_semantic.canonical_runner import (
    RealExecutionNotAuthorized,
    assert_real_execution_authorized,
    run_canonical_sources,
)
from study9_semantic.contracts import load_frozen_contracts


class CanonicalRunnerGuardTests(unittest.TestCase):
    def test_current_protocol_refuses_real_execution(self):
        contracts = load_frozen_contracts(ROOT)
        with self.assertRaises(RealExecutionNotAuthorized):
            assert_real_execution_authorized(contracts)

    def test_runner_refuses_before_external_spec_or_source_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "results"
            with patch(
                "study9_semantic.canonical_runner._build_specs",
                side_effect=AssertionError("external spec construction must remain unreachable"),
            ), patch(
                "study9_semantic.canonical_runner.verify_csv_source",
                side_effect=AssertionError("source verification must remain unreachable"),
            ):
                with self.assertRaises(RealExecutionNotAuthorized):
                    run_canonical_sources(
                        cucd_zip=Path(tmp) / "does-not-exist-cucd.zip",
                        aegissat_csv=Path(tmp) / "does-not-exist-aegis.csv",
                        unsw_zip=Path(tmp) / "does-not-exist-unsw.zip",
                        output_dir=output,
                    )
            self.assertFalse(output.exists())

    def test_nonexistent_paths_do_not_mask_closed_authorization_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            with self.assertRaises(RealExecutionNotAuthorized) as caught:
                run_canonical_sources(
                    cucd_zip=missing / "cucd.zip",
                    aegissat_csv=missing / "aegis.csv",
                    unsw_zip=missing / "unsw.zip",
                    output_dir=missing / "results",
                )
            self.assertIn("real Study 9 execution remains closed", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
