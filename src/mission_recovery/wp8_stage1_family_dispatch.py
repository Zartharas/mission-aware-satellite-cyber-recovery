from __future__ import annotations
from collections import Counter
from typing import Any
from .wp8_stage1_pilot import build_offline_stage1_plan, bind_stage1_runtime_observation

DECISION_ID="R-038"
EVENT_ADAPTERS={
 "E1":("command","stage1-command-pilot-adapter","stage_1_command_runtime_executor_runtime_validated","src.mission_recovery.wp8_command_runtime_executor","scripts/run_wp8_command_stage1_development.sh"),
 "E3":("recovery","stage1-recovery-pilot-adapter","stage_1_recovery_runtime_executor_runtime_validated","src.mission_recovery.wp8_recovery_runtime_executor","scripts/run_wp8_recovery_stage1_development.sh"),
 "E4":("observability","stage1-observability-pilot-adapter","stage_1_observability_runtime_executor_runtime_validated","src.mission_recovery.wp8_observability_evidence","scripts/run_wp8_observability_stage1_development.sh"),
}
COUNTS={"command":7,"recovery":4,"observability":1}

def validate_family_dispatch_contract(pilot:dict[str,Any])->None:
 r=pilot["stage_1_runner_contract"]; g=pilot["instrumentation_gate"]; st=g["component_status"]
 c=r["family_runtime_dispatch_adapter_contract"]
 if c["decision_id"]!=DECISION_ID: raise ValueError("family dispatch decision is not R-038")
 if c["adapter_module"]!="src.mission_recovery.wp8_stage1_family_dispatch": raise ValueError("adapter module changed")
 if c["binding_entrypoint"]!="src.mission_recovery.wp8_stage1_pilot.bind_stage1_runtime_observation": raise ValueError("binding entrypoint changed")
 if c["expected_stage1_family_counts"]!=COUNTS: raise ValueError("family counts changed")
 if c["factor_source"]!="wp8_pilot_design.cells" or c["seed_source"]!="stage_1_control_validity.seed": raise ValueError("factor/seed source changed")
 if c["actual_policy_source"]!="retained_runtime_execution_metadata": raise ValueError("actual policy source changed")
 if c["raw_metric_source"]!="retained_family_runtime_observation": raise ValueError("raw metric source changed")
 if c["offline_static_validation_complete"] is not True: raise ValueError("offline static validation incomplete")
 if c["pilot_mode_materialization_complete"] is not False: raise ValueError("pilot mode predeclared")
 if c["runtime_execution_performed"] or c["pilot_seed_consumed"] or c["pilot_data_generated"]: raise ValueError("R-038 crossed offline boundary")
 for eid,(fam,aid,gate,module,runner) in EVENT_ADAPTERS.items():
  d=r["dispatch_by_event_id"][eid]
  if d["runtime_family"]!=fam or d["development_executor"]!=runner: raise ValueError(f"{eid}: source dispatch changed")
  if st[gate] is not True: raise ValueError(f"{eid}: source runtime not validated")
  if d["pilot_executor_ready"] is not False: raise ValueError(f"{eid}: pilot executor predeclared")
 if st["stage_1_family_runtime_dispatch_adapters"] is not False: raise ValueError("dispatch gate predeclared")
 if g["pilot_execution_authorized"] is not False: raise ValueError("pilot authorization predeclared")

def build_offline_family_dispatch_matrix(pilot:dict[str,Any])->dict[str,Any]:
 validate_family_dispatch_contract(pilot)
 plan=build_offline_stage1_plan(pilot); rows=[]
 for x in plan["planned_cells"]:
  cell=x["cell"]; fam,aid,gate,module,runner=EVENT_ADAPTERS[cell["event_id"]]
  if x["dispatch"]["runtime_family"]!=fam: raise ValueError(f"{cell['cell_id']}: wrong family")
  rows.append({"position":x["position"],"cell_id":cell["cell_id"],"seed":plan["seed"],"event_id":cell["event_id"],"runtime_family":fam,"adapter_id":aid,"source_runtime_gate":gate,"source_runtime_executor":module,"source_development_runner":runner,"requested_policy_id":cell["policy_id"],"expected_effective_policy_id_for_acceptance_only":cell["expected_effective_policy_id"],"runtime_execution_authorized":False,"pilot_seed_consumed":False,"pilot_data_generated":False})
 counts=dict(Counter(x["runtime_family"] for x in rows))
 if counts!=COUNTS: raise ValueError(f"family counts changed: {counts}")
 return {"schema":1,"decision_id":DECISION_ID,"ordered_cell_ids":plan["ordered_cell_ids"],"family_counts":counts,"rows":rows,"runtime_execution_performed":False,"runtime_execution_authorized":False,"pilot_seed_consumed":False,"pilot_data_generated":False}

def blocked_adapter_request(pilot:dict[str,Any],cell_id:str,run_id:str)->dict[str,Any]:
 validate_family_dispatch_contract(pilot)
 cells={x["cell_id"]:x for x in pilot["cells"]}
 if cell_id not in cells or not run_id: raise ValueError("invalid Stage-1 adapter request")
 cell=cells[cell_id]; fam,aid,*_=EVENT_ADAPTERS[cell["event_id"]]
 return {"cell_id":cell_id,"run_id":run_id,"seed":int(pilot["stage_1_control_validity"]["seed"]),"event_id":cell["event_id"],"runtime_family":fam,"adapter_id":aid,"runtime_execution_authorized":False,"pilot_seed_consumed":False,"pilot_data_generated":False}

def require_pilot_dispatch_authorized(pilot:dict[str,Any])->None:
 g=pilot["instrumentation_gate"]
 if g["component_status"]["stage_1_family_runtime_dispatch_adapters"] is not True: raise PermissionError("Stage-1 family dispatch gate is not closed")
 if g["pilot_execution_authorized"] is not True: raise PermissionError("Stage-1 pilot execution is not authorized")

def validate_family_observation_envelope(pilot:dict[str,Any],cell_id:str,run_id:str,bundle:dict[str,Any])->None:
 cells={x["cell_id"]:x for x in pilot["cells"]}; cell=cells[cell_id]
 fam=EVENT_ADAPTERS[cell["event_id"]][0]; seed=int(pilot["stage_1_control_validity"]["seed"])
 expected={"run_id":run_id,"model_version":pilot["model_version"],"seed":seed,"mission_state_id":cell["mission_state_id"],"event_id":cell["event_id"],"policy_id":cell["policy_id"],"contact_condition_id":cell["contact_condition_id"],"evidence_condition_id":cell["evidence_condition_id"]}
 if bundle.get("factor_context")!=expected: raise ValueError("factor context differs from frozen cell")
 meta=bundle.get("execution_metadata")
 if not isinstance(meta,dict) or meta.get("effective_policy_id")!=cell["expected_effective_policy_id"]: raise ValueError("actual effective policy differs from frozen acceptance semantics")
 obs=bundle.get("runtime_observation")
 if not isinstance(obs,dict) or obs.get("family")!=fam: raise ValueError("runtime family differs from dispatch")
 if obs.get("development_preflight") is not False: raise ValueError("pilot observation cannot be development preflight")
 if obs.get("pilot_data") is not True: raise ValueError("pilot observation must mark pilot_data=true")

def bind_authorized_family_observation(*,pilot,toolchain,schema,cell_id,run_id,observation_bundle,snapshot_id,host_architecture=None):
 require_pilot_dispatch_authorized(pilot)
 validate_family_observation_envelope(pilot,cell_id,run_id,observation_bundle)
 return bind_stage1_runtime_observation(pilot=pilot,toolchain=toolchain,schema=schema,cell_id=cell_id,run_id=run_id,observation_bundle=observation_bundle,snapshot_id=snapshot_id,host_architecture=host_architecture)
