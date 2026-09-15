from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from zipfile import ZIP_STORED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from study9_semantic.canonical_runner import (
    CanonicalRunError,
    RealExecutionNotAuthorized,
    assert_real_execution_authorized,
    run_canonical_sources,
)
from study9_semantic.completions import PartialObservation
from study9_semantic.contracts import (
    CANONICAL_RUN_CODE_FREEZE_PATH,
    RUN_IDENTITY_BASE_PATHS,
    load_frozen_contracts,
)
from study9_semantic.independent_audit import clear_audit_caches
from study9_semantic.input_identity import InputIdentitySpec
from study9_semantic.selector_adapter import clear_selector_caches
from study9_semantic.state_projection import project_native_row as real_project_native_row


class CanonicalRunnerGuardTests(unittest.TestCase):
    def tearDown(self):
        clear_selector_caches()
        clear_audit_caches()

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

    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def _write_zip(cls, path: Path, member: str, data: bytes) -> tuple[str, str]:
        with ZipFile(path, "w", compression=ZIP_STORED) as archive:
            archive.writestr(member, data)
        return cls._sha256(path.read_bytes()), cls._sha256(data)

    @classmethod
    def _synthetic_specs(cls, root: Path) -> dict[str, InputIdentitySpec]:
        cucd_member = "Data/Raw/consolidated_dataset_raw.csv"
        cucd_data = b"A,B\n1,2\n3,4\n5,6\n"
        cucd_path = root / "cucd.zip"
        cucd_outer, cucd_artifact = cls._write_zip(cucd_path, cucd_member, cucd_data)

        aegis_data = b"A,B\n1,2\n3,4\n5,6\n"
        aegis_path = root / "AegisSat-AD.csv"
        aegis_path.write_bytes(aegis_data)

        unsw_member = "UNSW-IoTSAT dataset/UNSW_IoTSAT.csv"
        unsw_data = b"Position_Anomaly,Attack_Flag\n0,1\n0,0\n1,1\n"
        unsw_path = root / "unsw.zip"
        unsw_outer, unsw_artifact = cls._write_zip(unsw_path, unsw_member, unsw_data)

        return {
            "CUCD_ID_V3": InputIdentitySpec(
                dataset_id="CUCD_ID_V3",
                source_kind="ZIP_CSV_MEMBER",
                source_path=cucd_path,
                canonical_artifact_path=cucd_member,
                canonical_artifact_sha256=cucd_artifact,
                expected_rows=3,
                expected_columns=2,
                outer_container_sha256=cucd_outer,
            ),
            "AEGISSAT_2025": InputIdentitySpec(
                dataset_id="AEGISSAT_2025",
                source_kind="DIRECT_CSV",
                source_path=aegis_path,
                canonical_artifact_path="AegisSat-AD.csv",
                canonical_artifact_sha256=cls._sha256(aegis_data),
                expected_rows=3,
                expected_columns=2,
            ),
            "UNSW_IOTSAT_2026": InputIdentitySpec(
                dataset_id="UNSW_IOTSAT_2026",
                source_kind="ZIP_CSV_MEMBER",
                source_path=unsw_path,
                canonical_artifact_path=unsw_member,
                canonical_artifact_sha256=unsw_artifact,
                expected_rows=3,
                expected_columns=2,
                outer_container_sha256=unsw_outer,
            ),
        }

    def test_full_synthetic_runner_is_byte_deterministic_and_audited(self):
        contracts = load_frozen_contracts(ROOT)
        expected_outputs = tuple(contracts.execution_design["future_canonical_result_artifacts"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = self._synthetic_specs(root)
            output_a = root / "run-a"
            output_b = root / "run-b"
            with patch(
                "study9_semantic.canonical_runner.assert_real_execution_authorized",
                return_value=None,
            ), patch(
                "study9_semantic.canonical_runner._build_specs",
                return_value=specs,
            ):
                result_a = run_canonical_sources(
                    cucd_zip=root / "ignored-cucd.zip",
                    aegissat_csv=root / "ignored-aegis.csv",
                    unsw_zip=root / "ignored-unsw.zip",
                    output_dir=output_a,
                )
                result_b = run_canonical_sources(
                    cucd_zip=root / "ignored-cucd-2.zip",
                    aegissat_csv=root / "ignored-aegis-2.csv",
                    unsw_zip=root / "ignored-unsw-2.zip",
                    output_dir=output_b,
                )

            self.assertEqual(result_a["artifact_count"], 8)
            self.assertEqual(result_a["audit_status"], "MATCH")
            self.assertEqual(result_b["audit_status"], "MATCH")
            self.assertEqual(
                tuple(path.name for path in sorted(output_a.iterdir())),
                tuple(sorted(expected_outputs)),
            )
            for name in expected_outputs:
                self.assertEqual((output_a / name).read_bytes(), (output_b / name).read_bytes())

            run_manifest = json.loads((output_a / "run_manifest.json").read_text(encoding="utf-8"))
            identity_paths = tuple(
                item["path"] for item in run_manifest["reproducibility_identity"]["files"]
            )
            self.assertEqual(
                identity_paths,
                RUN_IDENTITY_BASE_PATHS + (CANONICAL_RUN_CODE_FREEZE_PATH,),
            )
            self.assertEqual(identity_paths[-1], CANONICAL_RUN_CODE_FREEZE_PATH)
            self.assertEqual(run_manifest["reproducibility_identity"]["algorithm"], "sha256")
            for item in run_manifest["reproducibility_identity"]["files"]:
                self.assertEqual(len(item["sha256"]), 64)
                self.assertGreater(item["size_bytes"], 0)

            mapping = json.loads((output_a / "mapping_matrix.json").read_text(encoding="utf-8"))
            coverage = json.loads((output_a / "coverage_summary.json").read_text(encoding="utf-8"))
            independent = json.loads((output_a / "independent_audit.json").read_text(encoding="utf-8"))
            self.assertEqual(independent["status"], "MATCH")
            self.assertEqual(independent["policy_independent"]["mapping_matrix"], mapping)
            self.assertEqual(independent["policy_independent"]["coverage_summary"], coverage)

            output_manifest = json.loads(
                (output_a / "output_sha256_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(output_manifest["algorithm"], "sha256")
            for item in output_manifest["artifacts"]:
                data = (output_a / item["path"]).read_bytes()
                self.assertEqual(item["size_bytes"], len(data))
                self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())

    def test_full_synthetic_runner_initializes_each_selector_path_once(self):
        contracts = load_frozen_contracts(ROOT)
        clear_selector_caches()
        clear_audit_caches()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = self._synthetic_specs(root)
            output = root / "bounded-init-run"
            with patch(
                "study9_semantic.canonical_runner.assert_real_execution_authorized",
                return_value=None,
            ), patch(
                "study9_semantic.canonical_runner._build_specs",
                return_value=specs,
            ), patch(
                "study9_semantic.selector_adapter.load_frozen_contracts",
                return_value=contracts,
            ) as canonical_loader, patch(
                "study9_semantic.independent_audit.load_frozen_contracts",
                return_value=contracts,
            ) as audit_loader:
                result = run_canonical_sources(
                    cucd_zip=root / "ignored-cucd.zip",
                    aegissat_csv=root / "ignored-aegis.csv",
                    unsw_zip=root / "ignored-unsw.zip",
                    output_dir=output,
                )

            self.assertEqual(result["artifact_count"], 8)
            self.assertEqual(result["audit_status"], "MATCH")
            self.assertEqual(canonical_loader.call_count, 1)
            self.assertEqual(audit_loader.call_count, 1)

    def test_full_synthetic_runner_detects_corrupted_canonical_projection(self):
        def corrupted_projector(plan, row):
            partial = real_project_native_row(plan, row)
            if plan.dataset_id != "UNSW_IOTSAT_2026":
                return partial
            return PartialObservation.build(
                known={"security_signal": True},
                unresolved=tuple(
                    name for name in partial.unresolved if name != "security_signal"
                ),
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = self._synthetic_specs(root)
            output = root / "corrupted-run"
            with patch(
                "study9_semantic.canonical_runner.assert_real_execution_authorized",
                return_value=None,
            ), patch(
                "study9_semantic.canonical_runner._build_specs",
                return_value=specs,
            ), patch(
                "study9_semantic.canonical_runner.project_native_row",
                side_effect=corrupted_projector,
            ):
                with self.assertRaises(CanonicalRunError) as caught:
                    run_canonical_sources(
                        cucd_zip=root / "ignored-cucd.zip",
                        aegissat_csv=root / "ignored-aegis.csv",
                        unsw_zip=root / "ignored-unsw.zip",
                        output_dir=output,
                    )
            self.assertIn("canonical/audit native-state grouping mismatch", str(caught.exception))
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
