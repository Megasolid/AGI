#!/usr/bin/env python3
"""Deterministic read-only verification for Citadel M2 staging task. Prints computed values; no writes."""
import argparse, hashlib, json, urllib.request

def canon(o): return json.dumps(o, sort_keys=True, separators=(",",":"), ensure_ascii=False)
def sha(b): return hashlib.sha256(b).hexdigest()
def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--task", default="citadel/tasks/cit-kilo-m2-20261031-11.json")
    a=ap.parse_args()
    base="https://raw.githubusercontent.com/Megasolid/AGI/%s/" % a.commit
    raw=get(base+a.task)
    task=json.loads(raw)
    body={k:v for k,v in task.items() if k not in ("task_hash","signature")}
    calc="sha256:"+sha(canon(body).encode("utf-8"))
    inputs=[]
    for i in task.get("inputs",[]):
        p=i["path"]
        try:
            b=get(base+p)
            text=b.decode("utf-8").replace("
","
")
            h="sha256:"+sha(text.encode("utf-8"))
            inputs.append({"path":p,"computed":h,"stated":i["sha256"],"match":h==i["sha256"]})
        except Exception as e:
            inputs.append({"path":p,"error":str(e),"match":False})
    staging_path=[x for x in task.get("inputs",[]) if x["path"].endswith("staging-evidence.json")]
    staging=None
    if staging_path:
        try:
            staging=json.loads(get(base+staging_path[0]["path"]))
        except Exception as e:
            staging={"error":str(e)}
    out={"task_id":task.get("task_id"),"task_canonical_sha256_computed":calc,
         "task_stated_hash":task.get("task_hash"),"task_hash_match":calc==task.get("task_hash"),
         "inputs":inputs,"all_inputs_match":all(x.get("match") for x in inputs),
         "staging_evidence":{"total":staging.get("post_apply_rows") if staging else None,
                              "all_pass":staging.get("all_pass") if staging else None,
                              "checks":len(staging.get("checks",[])) if staging else None,
                              "migration_apply_ok":(staging.get("migration_apply") or {}).get("ok") if staging else None,
                              "migration_rollback_ok":(staging.get("migration_rollback") or {}).get("ok") if staging else None},
         "signature_check":"not performed by deterministic script; inspect task.signature separately"}
    print(json.dumps(out,indent=1))
    return 0 if out["task_hash_match"] and out["all_inputs_match"] else 1
if __name__=="__main__": raise SystemExit(main())
