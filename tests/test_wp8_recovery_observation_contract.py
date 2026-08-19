import json, unittest
from pathlib import Path
from src.mission_recovery.primary_metrics import RECOVERY_CRITERIA
from src.mission_recovery.wp8_recovery_effect_contract import (
    build_recovery_cell_effect_contract,
)
from src.mission_recovery.wp8_recovery_observation_contract import (
    build_recovery_observation_matrix,
    build_recovery_observation_plan,
    derive_recovery_runtime_observation,
    require_recovery_observation_acceptance,
)

ROOT=Path(__file__).resolve().parents[1]
PILOT=json.loads((ROOT/"configs/wp8_pilot_design.json").read_text(encoding="utf-8"))

def valid(cell):
    c=build_recovery_cell_effect_contract(PILOT,cell)
    p=c["policy_evaluation"]; a=c["event_artifacts"]
    family=c["effect_dispatch"]["effect_family"]
    x={
        "actual_effective_policy_id":p["actual_effective_policy_id"],
        "selected_action":p["selected_action"],
        "event_slot_sha256":a["tampered_sha256"],
        "post_response_slot_sha256":a["tampered_sha256"],
        "rejected_sha256_absent":False,
        "temporary_recovery_state_absent":True,
        "rollback_request_emitted":False,
        "rollback_request_validated":False,
        "replacement_source_verified":False,
        "event_activation_ns":100,"policy_selection_ns":108,
        "event_success_ns":110,"policy_enforcement_ns":120,
        "post_response_slot_observed_ns":130,
        "authorized_noop_probe_observed_ns":140,
        "criteria_classification_ns":170,"run_end_ns":200,
        "authorized_noop_attempt_count":1,"authorized_noop_marker_delta":1,
    }
    if family=="rollback_request":
        x.update({
            "post_response_slot_sha256":a["approved_sha256"],
            "rejected_sha256_absent":True,
            "rollback_request_emitted":True,
            "rollback_request_validated":True,
            "replacement_source_verified":True,
        })
    if family=="command_gateway":
        x["command_gateway_observation"]={
            "matched_attacker_probe_count":2,"attacker_reset_marker_delta":0,
            "authorized_noop_attempt_count":1,"authorized_noop_marker_delta":1,
        }
        x["command_gateway_probe_observed_ns"]=135
    contained=family=="rollback_request"
    rows={}
    for i,k in enumerate(RECOVERY_CRITERIA):
        rows[k]={
            "available_current":True,"criterion_satisfied":True,
            "evidence_ref":f"unit:{cell}:{k}","observed_ns":145+i,
        }
    rows["approved_version"]["observed_ns"]=130
    rows["approved_version"]["criterion_satisfied"]=contained
    rows["recovery_manifest_complete"]["observed_ns"]=165
    x["recovery_criteria"]=rows
    return x

class RecoveryObservationContractTests(unittest.TestCase):
    def test_matrix_roles(self):
        m=build_recovery_observation_matrix(PILOT)
        got={r["cell_id"]:(r["effect_family"],
            r["update_containment_expected_for_acceptance_only"],
            r["command_path_mitigation_applicable"])
            for r in m["rows"]}
        self.assertEqual(got,{
            "R01":("observe_only",False,False),
            "R02":("rollback_request",True,False),
            "R03":("rollback_request",True,False),
            "R04":("command_gateway",False,True),
        })

    def test_success_values_not_frozen(self):
        for cell in ("R01","R02","R03","R04"):
            p=build_recovery_observation_plan(PILOT,cell)
            self.assertFalse(p["mo4_expected_value_frozen"])
            self.assertFalse(p["mo5_expected_value_frozen"])
            self.assertFalse(p["trusted_recovery_expected_value_frozen"])
            self.assertFalse(p["event_observer_can_gate_policy_response"])

    def test_valid_all_cells(self):
        expected={"R01":False,"R02":True,"R03":True,"R04":False}
        for cell in expected:
            d=derive_recovery_runtime_observation(
                pilot=PILOT,cell_id=cell,observation=valid(cell))
            require_recovery_observation_acceptance(d)
            self.assertEqual(d["containment"]["predicate"],expected[cell])
            self.assertEqual(d["trusted_recovery"]["predicate"],expected[cell])
            self.assertEqual(d["objective_results"]["MO-4"]["completed"],expected[cell])
            self.assertTrue(d["objective_results"]["MO-5"]["completed"])
            self.assertEqual(d["legitimate_commands"],{"attempted":1,"rejected":0})

    def test_r04_mitigation_not_containment(self):
        d=derive_recovery_runtime_observation(
            pilot=PILOT,cell_id="R04",observation=valid("R04"))
        self.assertTrue(d["command_path_mitigation"]["predicate"])
        self.assertFalse(d["command_path_mitigation"]["counts_as_e3_update_containment"])
        self.assertFalse(d["containment"]["predicate"])
        self.assertTrue(d["containment"]["right_censored_at_run_end"])

    def test_r04_t1_current_evidence_can_show_approved_false(self):
        d=derive_recovery_runtime_observation(
            pilot=PILOT,cell_id="R04",observation=valid("R04"))
        r=d["recovery_observations"]["approved_version"]
        self.assertTrue(r["available_current"])
        self.assertFalse(r["criterion_satisfied"])
        self.assertFalse(d["policy_time_visibility_used_as_classification_evidence"])

    def test_nonrecovery_does_not_force_mo5_false(self):
        for cell in ("R01","R04"):
            d=derive_recovery_runtime_observation(
                pilot=PILOT,cell_id=cell,observation=valid(cell))
            self.assertFalse(d["containment"]["predicate"])
            self.assertTrue(d["objective_results"]["MO-5"]["completed"])

    def test_contained_run_can_be_unverified_without_invalidity(self):
        x=valid("R02")
        x["recovery_criteria"]["required_telemetry_restored"][
            "criterion_satisfied"]=False
        d=derive_recovery_runtime_observation(
            pilot=PILOT,cell_id="R02",observation=x)
        require_recovery_observation_acceptance(d)
        self.assertTrue(d["containment"]["predicate"])
        self.assertFalse(d["trusted_recovery"]["predicate"])
        self.assertTrue(d["trusted_recovery"]["right_censored_at_run_end"])

    def test_satisfied_without_current_rejected(self):
        x=valid("R02")
        x["recovery_criteria"]["health_checks_passed"]["available_current"]=False
        with self.assertRaisesRegex(ValueError,"criterion_satisfied=true"):
            derive_recovery_runtime_observation(
                pilot=PILOT,cell_id="R02",observation=x)

    def test_event_observer_deadline_enforced(self):
        x=valid("R02"); x["event_success_ns"]=121
        with self.assertRaisesRegex(ValueError,"complete by enforcement"):
            derive_recovery_runtime_observation(
                pilot=PILOT,cell_id="R02",observation=x)

    def test_complete_manifest_cannot_predate_evidence(self):
        x=valid("R02")
        x["recovery_criteria"]["recovery_manifest_complete"]["observed_ns"]=140
        with self.assertRaisesRegex(ValueError,"manifest predates"):
            derive_recovery_runtime_observation(
                pilot=PILOT,cell_id="R02",observation=x)

    def test_offline_boundary(self):
        m=build_recovery_observation_matrix(PILOT)
        self.assertFalse(m["runtime_execution_authorized"])
        self.assertFalse(m["pilot_seed_consumed"])
        self.assertFalse(m["pilot_data_generated"])
        self.assertFalse(m["primary_metrics_emitted"])
        self.assertFalse(m["terminal_states_emitted"])

if __name__=="__main__": unittest.main()
