from __future__ import annotations
from collections import Counter
from copy import deepcopy
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
 materialized=c["pilot_mode_materialization_complete"]
 if materialized not in (False, True):
  raise ValueError("invalid pilot-mode materialization state")
 if materialized is True:
  pilot_mode=c.get("pilot_mode_contract")
  if not isinstance(pilot_mode,dict) or pilot_mode.get("decision_id")!="R-039":
   raise ValueError("pilot-mode materialization lacks R-039 contract")
 if c["runtime_execution_performed"] or c["pilot_seed_consumed"] or c["pilot_data_generated"]: raise ValueError("R-038 crossed offline boundary")
 for eid,(fam,aid,gate,module,runner) in EVENT_ADAPTERS.items():
  d=r["dispatch_by_event_id"][eid]
  if d["runtime_family"]!=fam or d["development_executor"]!=runner: raise ValueError(f"{eid}: source dispatch changed")
  if st[gate] is not True: raise ValueError(f"{eid}: source runtime not validated")

def build_offline_family_dispatch_matrix(pilot:dict[str,Any])->dict[str,Any]:
 validate_family_dispatch_contract(pilot)
 blocked=deepcopy(pilot); blocked["instrumentation_gate"]["pilot_execution_authorized"]=False
 plan=build_offline_stage1_plan(blocked); rows=[]
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

PILOT_MODE_DECISION_ID = "R-039"
PILOT_RUNTIME_PATH_BY_CELL = {
    "C01": "command_generic",
    "C02": "command_generic",
    "C03": "command_generic",
    "C04": "command_generic",
    "C05": "command_generic",
    "C06": "command_generic",
    "C07": "command_generic",
    "R01": "recovery_generic",
    "R02": "recovery_full_trusted",
    "R03": "recovery_full_trusted",
    "R04": "recovery_generic",
    "O01": "observability_generic",
}
PILOT_RUNTIME_PATH_FAMILY = {
    "command_generic": "command",
    "recovery_generic": "recovery",
    "recovery_full_trusted": "recovery",
    "observability_generic": "observability",
}

def validate_pilot_mode_materialization_contract(pilot: dict[str, Any]) -> None:
    validate_family_dispatch_contract(pilot)
    contract=pilot["stage_1_runner_contract"]["family_runtime_dispatch_adapter_contract"]["pilot_mode_contract"]
    if contract["decision_id"] != PILOT_MODE_DECISION_ID:
        raise ValueError("pilot-mode contract is not R-039")
    if int(contract["required_seed"]) != 101:
        raise ValueError("R-039 pilot seed changed")
    if contract["seed_source"] != "stage_1_control_validity.seed":
        raise ValueError("R-039 seed source changed")
    if contract["factor_source"] != "wp8_pilot_design.cells":
        raise ValueError("R-039 factor source changed")
    if contract["policy_selection_source"] != "src.mission_recovery.policies.evaluate_policy":
        raise ValueError("R-039 policy source changed")
    if contract["actual_effective_policy_required"] is not True:
        raise ValueError("R-039 actual effective policy requirement changed")
    if contract["expected_effective_policy_role"] != "post_observation_acceptance_only":
        raise ValueError("R-039 expected policy role changed")
    if contract["runtime_path_by_cell"] != PILOT_RUNTIME_PATH_BY_CELL:
        raise ValueError("R-039 runtime path mapping changed")
    sources=contract["runtime_path_sources"]
    if sources["recovery_generic"]["supported_cells"] != ["R01","R04"]:
        raise ValueError("R-039 generic recovery cells changed")
    if sources["recovery_full_trusted"]["supported_cells"] != ["R02","R03"]:
        raise ValueError("R-039 trusted recovery cells changed")
    if sources["recovery_full_trusted"]["full_all_ten_criteria_required"] is not True:
        raise ValueError("R-039 R02/R03 must retain all-ten-criteria proof")
    if sources["recovery_full_trusted"]["validated_runtime_source"] != "scripts/run_wp8_recovery_binding_preflight.sh":
        raise ValueError("R-039 trusted recovery source changed")
    if sources["observability_generic"]["supported_cells"] != ["O01"]:
        raise ValueError("R-039 observability cell changed")
    envelope=contract["pilot_observation_envelope"]
    if envelope["development_preflight"] is not False or envelope["pilot_data"] is not True:
        raise ValueError("R-039 pilot provenance changed")
    if envelope["raw_metric_inputs_from_observation_only"] is not True:
        raise ValueError("R-039 raw metrics cannot use expected values")
    if envelope["schema_binding_entrypoint"] != "src.mission_recovery.wp8_stage1_pilot.bind_stage1_runtime_observation":
        raise ValueError("R-039 binding entrypoint changed")
    if contract["offline_static_validation_complete"] is not True:
        raise ValueError("R-039 static validation incomplete")
    wiring_complete=contract["runtime_wiring_complete"]
    if wiring_complete not in (False, True):
        raise ValueError("R-039 runtime wiring state invalid")
    if wiring_complete is True:
        parent=pilot["stage_1_runner_contract"]["family_runtime_dispatch_adapter_contract"]
        r040=parent.get("runtime_wiring_contract")
        if not isinstance(r040,dict) or r040.get("decision_id")!="R-040":
            raise ValueError("R-039 runtime wiring lacks R-040 contract")
    if contract["runtime_execution_performed"] or contract["pilot_seed_consumed"] or contract["pilot_data_generated"]:
        raise ValueError("R-039 crossed offline boundary")

def pilot_runtime_path_for_cell(pilot: dict[str, Any], cell_id: str) -> dict[str, Any]:
    validate_pilot_mode_materialization_contract(pilot)
    cells={row["cell_id"]:row for row in pilot["cells"]}
    if cell_id not in cells:
        raise ValueError(f"unknown Stage-1 pilot cell: {cell_id}")
    cell=cells[cell_id]
    runtime_path=PILOT_RUNTIME_PATH_BY_CELL[cell_id]
    family=PILOT_RUNTIME_PATH_FAMILY[runtime_path]
    expected_family=EVENT_ADAPTERS[cell["event_id"]][0]
    if family != expected_family:
        raise ValueError(f"{cell_id}: runtime path disagrees with event family")
    return {"cell_id":cell_id,"event_id":cell["event_id"],"runtime_family":family,"runtime_path":runtime_path}

def build_blocked_pilot_runtime_request(pilot: dict[str, Any], *, cell_id: str, run_id: str) -> dict[str, Any]:
    validate_pilot_mode_materialization_contract(pilot)
    if not run_id:
        raise ValueError("pilot runtime request requires run_id")
    cells={row["cell_id"]:row for row in pilot["cells"]}
    if cell_id not in cells:
        raise ValueError(f"unknown Stage-1 pilot cell: {cell_id}")
    cell=cells[cell_id]
    route=pilot_runtime_path_for_cell(pilot,cell_id)
    seed=int(pilot["stage_1_control_validity"]["seed"])
    if seed != 101:
        raise ValueError("R-039 seed is not 101")
    return {
        "schema":1,
        "decision_id":PILOT_MODE_DECISION_ID,
        "classification":"WP8_STAGE1_PILOT_RUNTIME_REQUEST_BLOCKED",
        "cell_id":cell_id,
        "run_id":run_id,
        "seed":seed,
        "event_id":cell["event_id"],
        "mission_state_id":cell["mission_state_id"],
        "contact_condition_id":cell["contact_condition_id"],
        "evidence_condition_id":cell["evidence_condition_id"],
        "requested_policy_id":cell["policy_id"],
        "expected_effective_policy_id_for_acceptance_only":cell["expected_effective_policy_id"],
        "runtime_family":route["runtime_family"],
        "runtime_path":route["runtime_path"],
        "runtime_execution_authorized":False,
        "pilot_seed_consumed":False,
        "pilot_data_generated":False,
    }

def build_offline_pilot_mode_matrix(pilot: dict[str, Any]) -> dict[str, Any]:
    validate_pilot_mode_materialization_contract(pilot)
    blocked=deepcopy(pilot)
    blocked["instrumentation_gate"]["pilot_execution_authorized"]=False
    plan=build_offline_stage1_plan(blocked)
    rows=[
        build_blocked_pilot_runtime_request(
            pilot,cell_id=cell_id,run_id=f"offline-r039-{cell_id.lower()}-s101"
        )
        for cell_id in plan["ordered_cell_ids"]
    ]
    counts={}
    for row in rows:
        counts[row["runtime_path"]]=counts.get(row["runtime_path"],0)+1
    expected={
        "command_generic":7,
        "recovery_generic":2,
        "recovery_full_trusted":2,
        "observability_generic":1,
    }
    if counts != expected:
        raise ValueError(f"R-039 runtime-path counts changed: {counts!r}")
    return {
        "schema":1,
        "decision_id":PILOT_MODE_DECISION_ID,
        "seed":101,
        "ordered_cell_ids":plan["ordered_cell_ids"],
        "runtime_path_counts":counts,
        "rows":rows,
        "runtime_execution_performed":False,
        "runtime_execution_authorized":False,
        "pilot_seed_consumed":False,
        "pilot_data_generated":False,
    }
