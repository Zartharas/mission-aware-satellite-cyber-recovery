#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE="https://network.satnogs.org/api/observations/"
PARAMS={
  "start":"2026-06-01T00:00:00Z",
  "end":"2026-07-01T00:00:00Z",
  "satellite__norad_cat_id":"63235",
  "ground_station":"4242",
  "format":"json",
}
TARGET=(63235,4242)

def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    req=Request(BASE+"?"+urlencode(PARAMS),headers={"Accept":"application/json","User-Agent":"S8E-ECTV-001-filter-diagnostic/1.0"})
    with urlopen(req,timeout=60) as r:
        body=r.read()
        status=r.status
    data=json.loads(body)
    if not isinstance(data,list):
        raise SystemExit("unexpected response shape")
    returned_pairs=[]
    sat_ids=[]
    keys=set()
    for row in data:
        if not isinstance(row,dict): continue
        keys.update(row.keys())
        returned_pairs.append([row.get("norad_cat_id"),row.get("ground_station")])
        if "sat_id" in row:
            sat_ids.append(row.get("sat_id"))
        elif "satellite_id" in row:
            sat_ids.append(row.get("satellite_id"))

    source_matches=[]
    pats=[re.compile(r"norad_cat_id",re.I),re.compile(r"ground_station",re.I),re.compile(r"sat_id",re.I),re.compile(r"FilterSet"),re.compile(r"Observation.*Filter")]
    for path in sorted(a.source_root.rglob("*.py")):
        try: txt=path.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        lines=txt.splitlines()
        for i,line in enumerate(lines):
            if any(x.search(line) for x in pats) and ("observation" in str(path).lower() or "filter" in str(path).lower() or "serializer" in str(path).lower()):
                source_matches.append({
                  "path":str(path.relative_to(a.source_root)),
                  "line":i+1,
                  "context":[{"line":j+1,"text":lines[j]} for j in range(max(0,i-2),min(len(lines),i+3))]
                })

    out={
      "schema":1,
      "experiment_id":"S8E-ECTV-001",
      "stage":"FILTER_IDENTITY_DIAGNOSTIC",
      "request_parameters":PARAMS,
      "http_status":status,
      "response_sha256":sha(body),
      "records":len(data),
      "returned_pair_counts":{},
      "target_pair":list(TARGET),
      "all_rows_match_target_pair":all(tuple(x)==TARGET for x in returned_pairs),
      "distinct_returned_norad_cat_id":sorted({x[0] for x in returned_pairs},key=lambda x:(x is None,x)),
      "distinct_returned_ground_station":sorted({x[1] for x in returned_pairs},key=lambda x:(x is None,x)),
      "satellite_identity_field_present":bool(sat_ids),
      "distinct_returned_satellite_identity":sorted({x for x in sat_ids if x is not None}),
      "response_keys":sorted(keys),
      "source_matches":source_matches,
      "scope_boundary":{
        "timestamps_persisted":False,
        "duration_computed":False,
        "gap_computed":False,
        "recovery_endpoint_computed":False
      }
    }
    from collections import Counter
    c=Counter(tuple(x) for x in returned_pairs)
    out["returned_pair_counts"]={f"{k[0]}|{k[1]}":v for k,v in sorted(c.items(),key=lambda kv:str(kv[0]))}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "records":out["records"],
      "all_rows_match_target_pair":out["all_rows_match_target_pair"],
      "distinct_returned_norad_cat_id":out["distinct_returned_norad_cat_id"],
      "distinct_returned_ground_station":out["distinct_returned_ground_station"],
      "satellite_identity_field_present":out["satellite_identity_field_present"],
      "source_match_count":len(source_matches)
    },sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
