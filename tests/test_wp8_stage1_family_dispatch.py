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

if __name__=="__main__": unittest.main()
