#!/usr/bin/env python3
"""agi_conformance - beta conformance matrix for AGI Entelechy (C-beta1..C-beta8).

Runs against an isolated sandbox copy (never live state) and returns a per-check verdict. This is the beta
analogue of the gen3 C1-C6 matrix: it proves the DNA contract, runtime intents, recall, sensorium, budgets,
bridge scopes/approval locality and the SSE transport.

CLI:
    python runtime/agi_conformance.py --root <sandbox> [--out state/archive/evolution/beta-conformance-run.json]
"""
import argparse
import json
import pathlib
import shutil
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agi_bridge  # noqa: E402
import agi_runtime  # noqa: E402

SCHEMA = "agi-entelechy/conformance-matrix/1"


def _http(method, url, token=None, body=None, headers=None, timeout=8):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json", **({"Authorization": "Bearer " + token} if token else {}),
         **(headers or {})}
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with op.open(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()


def run(sandbox):
    root = pathlib.Path(sandbox).resolve()
    checks = []

    def ck(cid, name, ok, detail=""):
        checks.append({"id": cid, "name": name, "ok": bool(ok), "detail": str(detail)[:300]})

    dna = json.loads((root / "core/dna.v4.json").read_text(encoding="utf-8"))
    body = {k: v for k, v in dna.items() if k != "digest_sha256"}
    import hashlib
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    ck("C-beta1", "identity: Entelechy gen4 / DNA v4 / singleton gen_id", dna.get("schema") == "agi-dna/4"
       and dna["generation"]["name"] == "Entelechy" and dna["generation"]["dna_version"] == 4
       and dna["generation"]["gen_id"].startswith("ENTL-"), dna["generation"].get("gen_id"))
    ck("C-beta1b", "integrity: DNA canonical digest matches", digest == dna.get("digest_sha256"),
       (digest[:12], str(dna.get("digest_sha256"))[:12]))
    inv = dna.get("invariants") or []
    rules = (dna.get("reactive_dna") or {}).get("rules") or []
    ck("C-beta2", "DNA contract: I1-I9 + >=12 reactive rules", len(inv) >= 9 and len(rules) >= 12, (len(inv), len(rules)))

    rt = agi_runtime.Runtime(root)
    st = rt.status()
    ck("C-beta3", "runtime status + born sandbox", st.get("ok") and st.get("generation") == "Entelechy"
       and st.get("index_items", 0) > 0, st.get("index_items"))
    v = rt.index_vectors()
    rec = rt.recall("alive DNA passport seed", k=3)
    ck("C-beta4", "memory recall: FTS5 + vector RRF fusion", rec.get("fusion") == "rrf(fts5,hash-vector)"
       and len(rec.get("hits") or []) > 0 and v.get("backend") in ("hash-vector", "sqlite-vec"), v.get("backend"))

    q = rt.propose_intent("remember", {"text": "conformance write"}, nonce="conf-1")
    q2 = rt.propose_intent("remember", {"text": "conformance write"}, nonce="conf-1")
    guest = rt.approve_intent(q.get("id"), actor="guest")
    appr = rt.approve_intent(q.get("id"), actor="Master")
    again = rt.approve_intent(q.get("id"), actor="Master")
    denied = rt.approve_intent(rt.fetch("https://example.com").get("id"), actor="Master")
    ck("C-beta5", "intents: idempotent, Master-only, execute-once, fetch denied",
       q.get("status") == "pending" and q2.get("idempotent") and not guest.get("ok")
       and appr.get("executed") and not again.get("ok") and denied.get("status") == "denied")

    ck("C-beta6", "sensorium percept digest exposed", bool((st.get("sensorium") or {}).get("present")
                                                           and st["sensorium"].get("digest_sha256")))

    b = agi_bridge.Bridge(root)
    full_tok = b.init_token(("read", "write"))["token"]
    srv = agi_bridge.ThreadingHTTPServer(("127.0.0.1", 0), agi_bridge.make_handler(b))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    try:
        code, _, rr = _http("POST", base + "/mcp", full_tok, {"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        init = json.loads(rr)
        code2, _, rr2 = _http("POST", base + "/mcp", full_tok, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = json.loads(rr2).get("result", {}).get("tools", [])
        code3, _, rr3 = _http("POST", base + "/mcp", full_tok,
                              {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                               "params": {"name": "approve_intent", "arguments": {"id": q.get("id")}}})
        appr_remote = json.loads(rr3).get("error", {})
        read_tok = b.init_token(("read",))["token"]
        write_read = _http("POST", base + "/mcp", read_tok,
                           {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                            "params": {"name": "propose_intent", "arguments": {"action": "remember"}}})
        scope_err = json.loads(write_read[2]).get("error", {})
        loopback = srv.server_address[0] == "127.0.0.1"
    finally:
        srv.shutdown()
    ck("C-beta7", "bridge: MCP initialize/tools, approval local-only, write scope enforced, loopback",
       code == 200 and init.get("result", {}).get("protocolVersion") and len(tools) == 10
       and appr_remote.get("code") == -32003 and scope_err.get("code") == -32001 and loopback,
       {"tools": len(tools), "approval": appr_remote.get("code"), "scope": scope_err.get("code")})

    rt_lines = len((HERE / "agi_runtime.py").read_text(encoding="utf-8").splitlines())
    br_lines = len((HERE / "agi_bridge.py").read_text(encoding="utf-8").splitlines())
    dna_lines = len((root / "core/dna.v4.json").read_text(encoding="utf-8").splitlines())
    docs_root = HERE.parent
    docs = [p for p in ("README.beta.md", "INSTALL_PROMPT.beta.md", "USER_MANUAL.beta.md", "BETA-NOTES.md")
            if (docs_root / p).is_file()]
    ck("C-beta8", "budgets: runtime<=600, bridge<=520, DNA<=200 lines; docs<=4",
       rt_lines <= 600 and br_lines <= 520 and dna_lines <= 200 and len(docs) <= 4,
       (rt_lines, br_lines, dna_lines, len(docs)))

    passed = sum(1 for x in checks if x["ok"])
    return {"schema": SCHEMA, "sandbox": str(root), "checks": checks,
            "passed": passed, "total": len(checks),
            "verdict": "PASS" if passed == len(checks) else "ATTENTION"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Beta conformance matrix (C-beta1..C-beta8)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="state/archive/evolution/beta-conformance-run.json")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as td:
        cold = pathlib.Path(td) / "sandbox"
        shutil.copytree(a.root, cold)
        res = run(cold)
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({"verdict": res["verdict"], "passed": res["passed"], "total": res["total"],
                      "failed": [c["id"] for c in res["checks"] if not c["ok"]], "out": str(out)}, indent=1))
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
