#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from pathlib import Path

BASE="https://network.satnogs.org/api/observations/"
TARGET_NORAD=63235
TARGET_STATION=4242
PARAMS={
 "start":"2026-06-01T00:00:00Z",
 "end":"2026-07-01T00:00:00Z",
 "norad_cat_id":str(TARGET_NORAD),
 "ground_station":str(TARGET_STATION),
 "format":"json",
}

def main():
 import argparse
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
 req=Request(BASE+"?"+urlencode(PARAMS),headers={"Accept":"application/json","User-Agent":"S8E-ECTV-001-correct-filter-check/1.0"})
 with urlopen(req,timeout=60) as r:
  body=r.read(); status=r.status
 rows=json.loads(body)
 if not isinstance(rows,list): raise SystemExit("unexpected response shape")
 pairs=[]; sat_ids=[]
 for row in rows:
  if not isinstance(row,dict): raise SystemExit("non-object row")
  pairs.append([row.get("norad_cat_id"),row.get("ground_station")])
  sat_ids.append(row.get("sat_id"))
 out={
  "schema":1,
  "experiment_id":"S8E-ECTV-001",
  "stage":"CORRECT_FILTER_IDENTITY_CHECK",
  "request_parameters":PARAMS,
  "http_status":status,
  "response_sha256":hashlib.sha256(body).hexdigest(),
  "records":len(rows),
  "distinct_returned_norad_cat_id":sorted({x[0] for x in pairs}, key=lambda x:(x is None,x)),
  "distinct_returned_ground_station":sorted({x[1] for x in pairs}, key=lambda x:(x is None,x)),
  "distinct_returned_sat_id":sorted({x for x in sat_ids if x is not None}),
  "all_rows_match_requested_norad_and_station":all(x==[TARGET_NORAD,TARGET_STATION] for x in pairs),
  "scope_boundary":{"timestamps_persisted":False,"timing_endpoint_computed":False,"recovery_endpoint_computed":False}
 }
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps({k:out[k] for k in ("records","distinct_returned_norad_cat_id","distinct_returned_ground_station","distinct_returned_sat_id","all_rows_match_requested_norad_and_station")},sort_keys=True))
 return 0
if __name__=="__main__": raise SystemExit(main())
