#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from study6x.runtime.gate_evaluator import GATES, SIGNALS, evaluate_gate
from study6x.audit.reference_gate_evaluator import evaluate_gate_reference

AUTH_ID="S6X-CANONICAL-RUNTIME-AUTH-004"

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--authorization-record",required=True)
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--clean-artifact-sha256",required=True)
    ap.add_argument("--bad-artifact-sha256",required=True)
    ap.add_argument("--clean-signature-sha256",required=True)
    ap.add_argument("--bad-signature-sha256",required=True)
    ap.add_argument("--public-key-sha256",required=True)
    ap.add_argument("--clean-runtest-rc",type=int,required=True)
    ap.add_argument("--bad-runtest-rc",type=int,required=True)
    args=ap.parse_args()

    auth=json.loads(Path(args.authorization_record).read_text())
    if auth.get("authorization_id") != AUTH_ID:
        raise SystemExit("unexpected authorization id")
    if args.clean_runtest_rc != 0:
        raise SystemExit("clean compiled test suite did not pass")
    if args.bad_runtest_rc == 0:
        raise SystemExit("APPROVED_BAD_SOURCE compiled test suite unexpectedly passed")
    if args.clean_artifact_sha256 == args.bad_artifact_sha256:
        raise SystemExit("semantic fixture did not change designated LC artifact")

    out=Path(args.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    full={name:True for name in SIGNALS}
    records=[
        {"state_id":"CLEAN_APPROVED","objective_baseline_correct":True,
         "artifact_sha256":args.clean_artifact_sha256,"signature_sha256":args.clean_signature_sha256,
         "public_key_sha256":args.public_key_sha256,"assurance_signals":full},
        {"state_id":"APPROVED_BAD_SOURCE","objective_baseline_correct":False,
         "artifact_sha256":args.bad_artifact_sha256,"signature_sha256":args.bad_signature_sha256,
         "public_key_sha256":args.public_key_sha256,"assurance_signals":full},
    ]
    (out/"S6X_EVIDENCE_RECORDS_004.json").write_text(
        json.dumps({"schema":1,"experiment_id":"S6X-EAP-001","records":records},indent=2,sort_keys=True)+"\n"
    )

    fields=["block","case_id","state_id","unavailable_mask","gate",*SIGNALS,
            "objective_baseline_correct","primary_qualified","reference_qualified",
            "gate_mismatch","unsafe_qualified","correct_rejected","benign_availability_loss"]
    rows=[]
    for rec in records:
        for gate in GATES:
            e=rec["assurance_signals"]; p=evaluate_gate(gate,e); r=evaluate_gate_reference(gate,e)
            correct=rec["objective_baseline_correct"]
            rows.append({"block":"A_PAIRED_ARTIFACT_OBSERVABILITY",
                "case_id":f"A:{rec['state_id']}:{gate}","state_id":rec["state_id"],
                "unavailable_mask":"NONE","gate":gate,**{k:int(e[k]) for k in SIGNALS},
                "objective_baseline_correct":int(correct),"primary_qualified":int(p),
                "reference_qualified":int(r),"gate_mismatch":int(p!=r),
                "unsafe_qualified":int(p and not correct),"correct_rejected":int((not p) and correct),
                "benign_availability_loss":0})
    for mask in range(64):
        e={name:not bool(mask & (1<<i)) for i,name in enumerate(SIGNALS)}
        for gate in GATES:
            p=evaluate_gate(gate,e); r=evaluate_gate_reference(gate,e)
            rows.append({"block":"B_CLEAN_ARTIFACT_ASSURANCE_UNAVAILABILITY",
                "case_id":f"B:{mask:02d}:{gate}","state_id":"CLEAN_APPROVED",
                "unavailable_mask":f"0x{mask:02x}","gate":gate,**{k:int(e[k]) for k in SIGNALS},
                "objective_baseline_correct":1,"primary_qualified":int(p),
                "reference_qualified":int(r),"gate_mismatch":int(p!=r),
                "unsafe_qualified":0,"correct_rejected":int(not p),
                "benign_availability_loss":int(not p)})
    if len(rows)!=396: raise SystemExit(f"unexpected observation count {len(rows)}")
    with (out/"S6X_GATE_OBSERVATIONS_004.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(rows)
    mismatch=sum(int(r["gate_mismatch"]) for r in rows)
    summary={"schema":1,"experiment_id":"S6X-EAP-001","authorization_id":AUTH_ID,
        "observations":396,"block_a_rows":12,"block_b_rows":384,
        "primary_reference_gate_mismatches":mismatch,"clean_compiled_test_pass":True,
        "approved_bad_source_compiled_test_pass":False,"clean_bad_artifact_hash_distinct":True,
        "result_freeze_authorized":False,"manuscript_claim_use_authorized":False}
    (out/"S6X_SUMMARY_004.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("S6X_CANONICAL_POPULATION_GENERATION=PASS")
    print("observations=396")
    print(f"primary_reference_gate_mismatches={mismatch}")
    return 0 if mismatch==0 else 1

if __name__=="__main__":
    raise SystemExit(main())
