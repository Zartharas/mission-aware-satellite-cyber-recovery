import json, unittest
from copy import deepcopy
from pathlib import Path
from src.mission_recovery.wp8_stage1_family_dispatch import *
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/"configs/wp8_pilot_design.json").read_text())

class T(unittest.TestCase):
 def test_contract_and_matrix(self):
  validate_family_dispatch_contract(P)
  m=build_offline_family_dispatch_matrix(P)
  self.assertEqual(m["ordered_cell_ids"],["C05","R04","C04","R01","R03","C02","R02","C03","O01","C07","C01","C06"])
  self.assertEqual(m["family_counts"],{"command":7,"recovery":4,"observability":1})
  self.assertFalse(m["runtime_execution_performed"]); self.assertFalse(m["pilot_seed_consumed"]); self.assertFalse(m["pilot_data_generated"])
 def test_blocked_request(self):
  r=blocked_adapter_request(P,"C05","unit-r038-c05")
  self.assertEqual(r["seed"],101); self.assertEqual(r["runtime_family"],"command"); self.assertFalse(r["pilot_seed_consumed"])
  with self.assertRaisesRegex(PermissionError,"dispatch gate"):
   require_pilot_dispatch_authorized(P)
 def test_envelope_three_families(self):
  cells={x["cell_id"]:x for x in P["cells"]}
  for cid in ("C05","R04","O01"):
   c=cells[cid]; rid="unit-"+cid.lower(); fam=EVENT_ADAPTERS[c["event_id"]][0]
   b={"factor_context":{"run_id":rid,"model_version":P["model_version"],"seed":101,"mission_state_id":c["mission_state_id"],"event_id":c["event_id"],"policy_id":c["policy_id"],"contact_condition_id":c["contact_condition_id"],"evidence_condition_id":c["evidence_condition_id"]},"execution_metadata":{"effective_policy_id":c["expected_effective_policy_id"]},"runtime_observation":{"family":fam,"development_preflight":False,"pilot_data":True}}
   validate_family_observation_envelope(P,cid,rid,b)
 def test_envelope_rejects_wrong_policy_and_dev(self):
  c=next(x for x in P["cells"] if x["cell_id"]=="C05"); rid="unit-c05"
  b={"factor_context":{"run_id":rid,"model_version":P["model_version"],"seed":101,"mission_state_id":c["mission_state_id"],"event_id":"E1","policy_id":"P7","contact_condition_id":"C0","evidence_condition_id":"T0"},"execution_metadata":{"effective_policy_id":"P4"},"runtime_observation":{"family":"command","development_preflight":False,"pilot_data":True}}
  with self.assertRaisesRegex(ValueError,"actual effective policy"): validate_family_observation_envelope(P,"C05",rid,b)
  b["execution_metadata"]["effective_policy_id"]="P2"; b["runtime_observation"]["development_preflight"]=True; b["runtime_observation"]["pilot_data"]=False
  with self.assertRaisesRegex(ValueError,"development preflight"): validate_family_observation_envelope(P,"C05",rid,b)
 def test_future_authorization_needs_both_gates(self):
  p=deepcopy(P); p["instrumentation_gate"]["component_status"]["stage_1_family_runtime_dispatch_adapters"]=True
  with self.assertRaisesRegex(PermissionError,"pilot execution"): require_pilot_dispatch_authorized(p)

 def test_r039_pilot_runtime_path_matrix(self):
  validate_pilot_mode_materialization_contract(P)
  matrix=build_offline_pilot_mode_matrix(P)
  self.assertEqual(
   matrix["ordered_cell_ids"],
   ["C05","R04","C04","R01","R03","C02","R02","C03","O01","C07","C01","C06"],
  )
  self.assertEqual(
   matrix["runtime_path_counts"],
   {"command_generic":7,"recovery_generic":2,"recovery_full_trusted":2,"observability_generic":1},
  )
  self.assertFalse(matrix["runtime_execution_performed"])
  self.assertFalse(matrix["pilot_seed_consumed"])
  self.assertFalse(matrix["pilot_data_generated"])

 def test_r039_recovery_anchor_routing(self):
  self.assertEqual(pilot_runtime_path_for_cell(P,"R01")["runtime_path"],"recovery_generic")
  self.assertEqual(pilot_runtime_path_for_cell(P,"R04")["runtime_path"],"recovery_generic")
  self.assertEqual(pilot_runtime_path_for_cell(P,"R02")["runtime_path"],"recovery_full_trusted")
  self.assertEqual(pilot_runtime_path_for_cell(P,"R03")["runtime_path"],"recovery_full_trusted")

 def test_r039_blocked_request_preserves_seed_101(self):
  row=build_blocked_pilot_runtime_request(P,cell_id="R03",run_id="offline-r039-r03-s101")
  self.assertEqual(row["seed"],101)
  self.assertEqual(row["runtime_family"],"recovery")
  self.assertEqual(row["runtime_path"],"recovery_full_trusted")
  self.assertFalse(row["runtime_execution_authorized"])
  self.assertFalse(row["pilot_seed_consumed"])
  self.assertFalse(row["pilot_data_generated"])

 def test_r039_expected_policy_is_acceptance_only(self):
  contract=P["stage_1_runner_contract"]["family_runtime_dispatch_adapter_contract"]["pilot_mode_contract"]
  self.assertTrue(contract["actual_effective_policy_required"])
  self.assertEqual(contract["expected_effective_policy_role"],"post_observation_acceptance_only")
  self.assertTrue(contract["pilot_observation_envelope"]["raw_metric_inputs_from_observation_only"])

 def test_r039_runtime_wiring_and_authorization_remain_blocked(self):
  contract=P["stage_1_runner_contract"]["family_runtime_dispatch_adapter_contract"]["pilot_mode_contract"]
  self.assertTrue(contract["offline_static_validation_complete"])
  self.assertFalse(contract["runtime_wiring_complete"])
  self.assertFalse(P["instrumentation_gate"]["component_status"]["stage_1_family_runtime_dispatch_adapters"])
  self.assertFalse(P["instrumentation_gate"]["pilot_execution_authorized"])

if __name__=="__main__": unittest.main()
