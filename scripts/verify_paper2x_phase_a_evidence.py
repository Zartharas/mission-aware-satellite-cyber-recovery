#!/usr/bin/env python3
"""P2X Phase-A COSMOS evidence intake. A machine check is NOT independent visual verification."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
PIN="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
def check(ok,reason):
    if not ok:raise SystemExit("P2X_A_COSMOS_EVIDENCE_HOLD_"+reason)

if len(sys.argv)==2 and sys.argv[1]=="--check-template":
    p=ROOT/"paper2x/phase_a/COSMOS_GROUND_OBSERVATION_TEMPLATE.json"
    j=json.loads(p.read_text(encoding="utf-8"))
    check(j["schema"]==1 and j["experiment_id"]=="P2X-NOS3-RG-001","TEMPLATE_SCHEMA")
    check(j["session_id"] is None and j["observed_utc"] is None,"TEMPLATE_MUST_BE_UNFILLED")
    check(all(j["ground"][x] is None for x in (
      "radio_tx_bytes_before","radio_tx_bytes_after","radio_rx_bytes_before","radio_rx_bytes_after",
      "counter_before","counter_after","cfs_console_event_observed")),"NO_INVENTED_OBSERVATIONS")
    check(j["pin_nos3"]==PIN,"TEMPLATE_PIN")
    check(j["scope"]["independent_visual_review_completed"] is False,"TEMPLATE_REVIEW_GATE")
    print("P2X_A_UNFILLED_EVIDENCE_TEMPLATE=PASS")
    print("PHASE_A_COSMOS_TELEMETRY=NOT_OBSERVED")
    raise SystemExit(0)
if len(sys.argv)!=2:
    raise SystemExit("usage: python scripts/verify_paper2x_phase_a_evidence.py --check-template | PATH_TO_EVIDENCE_DIR")
folder=Path(sys.argv[1]).expanduser().resolve()
check(folder.is_dir(),"EVIDENCE_DIRECTORY")
partial=folder/"phase-a-partial-report.json"
ground=folder/"ground-observation.json"
check(partial.is_file(),"A1_PARTIAL_REPORT_MISSING")
check(ground.is_file(),"A2_OPERATOR_RECORD_MISSING")
a=json.loads(partial.read_text(encoding="utf-8"))
g=json.loads(ground.read_text(encoding="utf-8"))
check(a.get("experiment_id")=="P2X-NOS3-RG-001" and g.get("experiment_id")=="P2X-NOS3-RG-001","EXPERIMENT_ID")
check(a.get("pin_nos3")==PIN and g.get("pin_nos3")==PIN,"PIN_DRIFT")
check(a.get("classification")=="PHASE_A_PARTIAL_CFS_INGEST_PROOF__COSMOS_GROUND_CONFIRMATION_OPEN","A1_CLASSIFICATION")
check(a.get("internal_cfs_noop_increment")==1 and a.get("COSMOS_to_cFS_to_ground_telemetry_observed") is False,"A1_IS_NOT_COSMOS")
check(g.get("schema")==1 and isinstance(g.get("session_id"),str) and g["session_id"].strip(),"GROUND_SESSION_ID")
check(isinstance(g.get("observed_utc"),str) and g["observed_utc"].strip(),"GROUND_OBSERVATION_TIMESTAMP")
check(g.get("classification")=="COSMOS_GROUND_EVIDENCE_OPERATOR_RECORD_NOT_YET_OBSERVED","NON_AUTOMATIC_ACCEPTANCE")
v=g["ground"]
fixed={"ground_system":"COSMOS4_on_pinned_NOS3","radio_target":"CFS_RADIO",
"enable_output_command":"TO_ENABLE_OUTPUT","dest_ip":"radio_sim","dest_port":5011,
"noop_target":"CFS_RADIO","noop_command":"CFE_ES_NOOP","telemetry_target":"CFS_RADIO",
"telemetry_counter_field":"CMDCOUNTER"}
for k,value in fixed.items():check(v.get(k)==value,"PINNED_GROUND_FIELD_"+k)
for before,after in [
("radio_tx_bytes_before","radio_tx_bytes_after"),
("radio_rx_bytes_before","radio_rx_bytes_after"),
("counter_before","counter_after")]:
    x,y=v.get(before),v.get(after)
    check(type(x) is int and type(y) is int and 0<=x<y,"MEASUREMENT_MISSING_OR_NOT_INCREASING_"+before)
check(v["counter_after"]-v["counter_before"]==1,"NOOP_COUNTER_NOT_EXACTLY_ONE")
check(v.get("cfs_console_event_observed") is True,"CFS_EVENT_NOT_RECORDED")
check(g.get("scope",{}).get("fault_injection") is False and
      g["scope"].get("primary_scientific_results") is False and
      g["scope"].get("independent_visual_review_completed") is False,"SCOPE_VIOLATION")
evidence=[]
for key,filename in g["evidence_files"].items():
    check(isinstance(filename,str) and filename and "/" not in filename and "\\" not in filename,"INVALID_EVIDENCE_FILE_"+key)
    p=folder/filename
    check(p.is_file() and p.stat().st_size>=150,"EVIDENCE_FILE_MISSING_OR_EMPTY_"+key)
    if filename.lower().endswith((".png",".jpg",".jpeg")):
        check(p.stat().st_size>=1024,"SMALL_SCREENSHOT_"+key)
    evidence.append({"purpose":key,"file":filename,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size":p.stat().st_size})
command=(folder/g["evidence_files"]["ground_command_log"]).read_text(encoding="utf-8",errors="replace")
for marker in ("CFS_RADIO","TO_ENABLE_OUTPUT","CFE_ES_NOOP"):
    check(marker in command,"GROUND_COMMAND_LOG_MARKER_"+marker)
inventory={"schema":1,"experiment_id":"P2X-NOS3-RG-001",
"classification":"CANDIDATE_FOR_INDEPENDENT_VISUAL_REVIEW__PHASE_A_NOT_YET_ACCEPTED",
"pin_nos3":PIN,"A1_partial_report_sha256":hashlib.sha256(partial.read_bytes()).hexdigest(),
"A2_observation_record_sha256":hashlib.sha256(ground.read_bytes()).hexdigest(),
"evidence":evidence,"COSMOS_ground_observation_is_operator_recorded":True,
"independent_visual_review_completed":False,"scientific_experiment_data":False}
out=folder/"phase-a-review-inventory.json"
out.write_text(json.dumps(inventory,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P2X_A_EVIDENCE_FILES_AND_METADATA=PASS")
print("P2X_A_STATUS=CANDIDATE_FOR_INDEPENDENT_VISUAL_REVIEW_ONLY")
print("P2X_A_INVENTORY="+str(out))
