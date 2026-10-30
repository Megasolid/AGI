#!/usr/bin/env python3
"""agi_conformance - beta conformance matrix for AGI Entelechy (C-beta1..C-beta22).

Runs against an isolated sandbox copy (never live state) and returns a per-check verdict. This is the beta
analogue of the gen3 C1-C6 matrix: it proves the DNA contract, runtime intents, recall, sensorium, budgets,
bridge scopes/approval locality and the SSE transport.

CLI:
    python runtime/agi_conformance.py --root <sandbox> [--out state/archive/evolution/beta-conformance-run.json]
"""
import argparse
import json
import pathlib
import secrets
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
import agi_master  # noqa: E402
import agi_migrate  # noqa: E402
import agi_passport  # noqa: E402
import agi_policy  # noqa: E402
import agi_runtime  # noqa: E402
import agi_seats  # noqa: E402
import agi_tunnel  # noqa: E402

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


def run(sandbox, include_stability=True):
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

    conf_nonce = "conf-" + secrets.token_hex(6)
    q = rt.propose_intent("remember", {"text": "conformance write"}, nonce=conf_nonce)
    q2 = rt.propose_intent("remember", {"text": "conformance write"}, nonce=conf_nonce)
    guest = rt.approve_intent(q.get("id"), actor="guest")
    appr = rt.approve_intent(q.get("id"), actor="Master")
    again = rt.approve_intent(q.get("id"), actor="Master")
    denied = rt.approve_intent(rt.fetch("https://example.com/conf/" + conf_nonce).get("id"), actor="Master")
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
       code == 200 and init.get("result", {}).get("protocolVersion") and len(tools) >= 12
       and appr_remote.get("code") == -32003 and scope_err.get("code") == -32001 and loopback,
       {"tools": len(tools), "approval": appr_remote.get("code"), "scope": scope_err.get("code")})

    rt_lines = len((HERE / "agi_runtime.py").read_text(encoding="utf-8").splitlines())
    br_lines = len((HERE / "agi_bridge.py").read_text(encoding="utf-8").splitlines())
    dna_lines = len((root / "core/dna.v4.json").read_text(encoding="utf-8").splitlines())
    docs_root = HERE.parent
    docs = [p for p in ("README.beta.md", "INSTALL_PROMPT.beta.md", "USER_MANUAL.beta.md", "BETA-NOTES.md")
            if (docs_root / p).is_file()]
    ck("C-beta8", "budgets: runtime<=600, bridge<=560, DNA<=200 lines; docs<=4",
       rt_lines <= 600 and br_lines <= 560 and dna_lines <= 200 and len(docs) <= 4,
       (rt_lines, br_lines, dna_lines, len(docs)))

    # beta.5: event bus, migration read-only dry-run, tunnel plan (never executes)
    be = agi_bridge.Bridge(root)
    be.queue_intent({"action": "remember", "args": {"text": "conformance event"}, "nonce": "conf-evt"})
    ev = be.replay(0)
    ck("C-beta9", "event bus: intents are published and replayable",
       len(ev) >= 1 and any(e["type"] == "intent_queued" for e in ev), len(ev))
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "source"
        (src / "memory").mkdir(parents=True)
        (src / "memory" / "MEMORY.md").write_text("p-test\t2026-10-30 conformance memory line\n", encoding="utf-8")
        before = (src / "memory" / "MEMORY.md").read_text(encoding="utf-8")
        mig = agi_migrate.run(src, root, apply=False)
        after = (src / "memory" / "MEMORY.md").read_text(encoding="utf-8")
        ck("C-beta10", "migration dry-run is read-only and target-checked",
           mig.get("ok") and mig.get("applied") == 0 and mig.get("source_unchanged") and before == after, mig.get("error"))
    tchk = agi_tunnel.check()
    tplan = agi_tunnel.plan(port=8766)
    ck("C-beta11", "tunnel helper plans only (security policy, no execution)",
       isinstance(tchk.get("any_available"), bool) and len(tchk.get("security") or []) >= 3
       and "never" in (tplan.get("note") or "").lower(), tchk.get("verdict"))

    # beta.6/beta.7: device-key seat ceremony (ed25519 or hmac) + unbounded event window
    run_tag = secrets.token_hex(3)
    seat_member = "conf-seat-" + run_tag
    ed_member = "conf-ed25519-" + run_tag
    remote_member = "conf-remote-seat-" + run_tag
    ss = agi_seats.Seats(root)
    en = ss.enroll(seat_member)
    ch = ss.challenge(seat_member)
    proof = (agi_seats.Seats.sign_with_key(en.get("device_key"), seat_member, ch.get("nonce"))
             if en.get("mode") == "ed25519"
             else agi_seats.Seats.hmac_proof(en.get("device_key"), seat_member, ch.get("nonce")))
    login = ss.login(seat_member, ch.get("nonce"), proof)
    replay = ss.login(seat_member, ch.get("nonce"), proof)
    seat_status = ss.status()
    ck("C-beta12", "seat ceremony: enroll, challenge-response, replay blocked, no key material in status",
       en.get("ok") and login.get("ok") and not replay.get("ok")
       and any(x.get("member") == seat_member and x.get("status") == "active" for x in seat_status.get("seats", []))
       and "key_secret" not in json.dumps(seat_status), (login.get("status"), replay.get("error")))
    sse_bridge = agi_bridge.Bridge(root)
    sse_tok = sse_bridge.init_token(("read",))["token"]
    sse_srv = agi_bridge.ThreadingHTTPServer(("127.0.0.1", 0), agi_bridge.make_handler(sse_bridge))
    threading.Thread(target=sse_srv.serve_forever, daemon=True).start()
    sse_base = "http://127.0.0.1:%d" % sse_srv.server_address[1]
    try:
        t0 = time.time()
        code_sse, _, body_sse = _http("GET", sse_base + "/mcp?window=1", sse_tok, None,
                                      {"Accept": "text/event-stream"}, timeout=8)
        sse_elapsed = time.time() - t0
    finally:
        sse_srv.shutdown()
    ck("C-beta13", "unbounded window support: ?window=1 closes, window=0 is unbounded",
       code_sse == 200 and sse_elapsed < 5.0 and agi_bridge.SSE_UNBOUNDED == 0.0
       and agi_bridge.SSE_DEFAULT_WINDOW > 0, (code_sse, round(sse_elapsed, 2)))

    # beta.7: ed25519 public-key seats, Master ceremony, remote seat tools, rollback proof
    by = agi_seats.Seats(root)
    en2 = by.enroll(ed_member)
    ch2 = by.challenge(ed_member)
    proof2 = (agi_seats.Seats.sign_with_key(en2.get("device_key"), ed_member, ch2.get("nonce"))
              if en2.get("mode") == "ed25519" else agi_seats.Seats.hmac_proof(en2.get("device_key"), ed_member, ch2.get("nonce")))
    login2 = by.login(ed_member, ch2.get("nonce"), proof2)
    st2 = by.status()
    seat2 = [x for x in st2.get("seats", []) if x.get("member") == ed_member]
    ck("C-beta14", "seats: ed25519 public-key mode (or hmac fallback), replay blocked",
       en2.get("ok") and login2.get("ok") and (seat2 and seat2[0].get("mode") in ("ed25519", "hmac"))
       and not by.login(ed_member, ch2.get("nonce"), proof2).get("ok"), (en2.get("mode"), login2.get("status")))

    if agi_master.HAVE_CRYPTO:
        mc = agi_master.ceremony(root)
        ident = agi_master.identity(root)
        mfile = root / "state" / "master-test.txt"
        mfile.write_text("master ceremony test", encoding="utf-8")
        ms = agi_master.sign_file(root, mfile)
        mv = agi_master.verify_file(root, mfile, ms.get("sig_file"))
        mfile.write_text("tampered", encoding="utf-8")
        mt = agi_master.verify_file(root, mfile, ms.get("sig_file"))
        ck("C-beta15", "Master Ed25519 ceremony: sign/verify, tamper rejected",
           (mc.get("ok") or ident.get("ok")) and ms.get("ok") and mv.get("ok") and not mt.get("ok"),
           (mc.get("ok"), ms.get("ok"), mv.get("ok"), mt.get("ok")))
    else:
        ck("C-beta15", "Master Ed25519 ceremony skipped (cryptography absent)", True, "skipped")

    rb = agi_bridge.Bridge(root)
    rb_tok = rb.init_token(("read", "write"))["token"]
    rb_srv = agi_bridge.ThreadingHTTPServer(("127.0.0.1", 0), agi_bridge.make_handler(rb))
    threading.Thread(target=rb_srv.serve_forever, daemon=True).start()
    rb_base = "http://127.0.0.1:%d" % rb_srv.server_address[1]
    try:
        _, _, lr = _http("POST", rb_base + "/mcp", rb_tok, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        rtools = json.loads(lr).get("result", {}).get("tools", [])
        _, _, cr = _http("POST", rb_base + "/mcp", rb_tok,
                         {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                          "params": {"name": "seat_challenge", "arguments": {"member": ed_member}}})
        rchal = json.loads(((json.loads(cr).get("result") or {}).get("content") or [{}])[0].get("text", "{}"))
        rproof = (agi_seats.Seats.sign_with_key(en2.get("device_key"), ed_member, rchal.get("nonce"))
                  if en2.get("mode") == "ed25519" else agi_seats.Seats.hmac_proof(en2.get("device_key"), ed_member, rchal.get("nonce")))
        _, _, lr2 = _http("POST", rb_base + "/mcp", rb_tok,
                          {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                           "params": {"name": "seat_login", "arguments": {"member": ed_member,
                                                                          "nonce": rchal.get("nonce"), "proof": rproof}}})
        rlogin = json.loads(((json.loads(lr2).get("result") or {}).get("content") or [{}])[0].get("text", "{}"))
    finally:
        rb_srv.shutdown()
    ck("C-beta16", "remote seat tools over MCP (challenge + signed login)",
       {t["name"] for t in rtools} >= {"seat_challenge", "seat_login"} and rchal.get("ok") and rlogin.get("ok"),
       (len(rtools), rlogin.get("error")))

    snap = agi_migrate.snapshot_db(root)
    with tempfile.TemporaryDirectory() as td:
        src2 = pathlib.Path(td) / "src"
        (src2 / "memory").mkdir(parents=True)
        (src2 / "memory" / "MEMORY.md").write_text("rollback\tline\n", encoding="utf-8")
        agi_migrate.run(src2, root, apply=True, limit=1)
    restored = agi_migrate.restore_db(root, snap.get("snapshot"))
    ck("C-beta17", "migration rollback proof: snapshot -> apply -> restore sha matches",
       snap.get("ok") and restored.get("ok") and restored.get("sha256") == snap.get("sha256"),
       (snap.get("sha256"), restored.get("sha256")))

    # beta.8: remote enrollment + Master-signed passports
    b8 = agi_bridge.Bridge(root)
    tok8 = b8.init_token(("read", "write"))["token"]
    srv8 = agi_bridge.ThreadingHTTPServer(("127.0.0.1", 0), agi_bridge.make_handler(b8))
    threading.Thread(target=srv8.serve_forever, daemon=True).start()
    base8 = "http://127.0.0.1:%d" % srv8.server_address[1]
    try:
        _, _, tl = _http("POST", base8 + "/mcp", tok8, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        tools8 = {t["name"] for t in (json.loads(tl).get("result") or {}).get("tools", [])}
        _, _, er = _http("POST", base8 + "/mcp", tok8,
                         {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                          "params": {"name": "seat_enroll", "arguments": {"member": remote_member,
                                                                          "mode": "auto"}}})
        enrolled = json.loads(((json.loads(er).get("result") or {}).get("content") or [{}])[0].get("text", "{}"))
        read8 = b8.init_token(("read",))["token"]
        _, _, er2 = _http("POST", base8 + "/mcp", read8,
                          {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                           "params": {"name": "seat_enroll", "arguments": {"member": remote_member + "-2"}}})
        scope8 = json.loads(er2).get("error", {})
        if agi_master.HAVE_CRYPTO:
            if not agi_master.identity(root).get("ok"):
                agi_master.ceremony(root)
            p8 = agi_passport.issue(root, remote_member, note="conformance")
            v8 = agi_passport.verify(root, remote_member)
            _, _, pv = _http("POST", base8 + "/mcp", read8,
                             {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                              "params": {"name": "passport_verify", "arguments": {"member": remote_member}}})
            pvres = json.loads(((json.loads(pv).get("result") or {}).get("content") or [{}])[0].get("text", "{}"))
        else:
            p8, v8, pvres = {"ok": True}, {"ok": True}, {"ok": True}
    finally:
        srv8.shutdown()
    ck("C-beta18", "remote seat enrollment over MCP (write scope enforced; key once)",
       {"seat_enroll", "seat_status", "passport_list", "passport_verify"} <= tools8
       and enrolled.get("ok") and scope8.get("code") == -32001,
       (enrolled.get("error"), scope8.get("code")))
    ck("C-beta19", "Master-signed passport: issue, verify, cross-checks (skipped without cryptography)",
       p8.get("ok") and v8.get("ok") and all((v8.get("checks") or {}).values()) and pvres.get("ok"),
       (p8.get("error"), v8.get("error")))

    # beta.9: ML-DSA dual signing, remote issuance policy gate, stability gate
    ident_now = agi_master.identity(root)
    if agi_master.HAVE_MLDSA and (ident_now.get("ident") or {}).get("mldsa"):
        dfile = root / "state" / "dual-sign-test.txt"
        dfile.write_text("dual signing test", encoding="utf-8")
        ds = agi_master.sign_file(root, dfile)
        dv = agi_master.verify_file(root, dfile, ds.get("sig_file"))
        dfile.write_text("tampered", encoding="utf-8")
        dt = agi_master.verify_file(root, dfile, ds.get("sig_file"))
        ck("C-beta20", "Master dual signing (Ed25519 + ML-DSA-65), tamper rejected",
           ds.get("ok") and "ml-dsa-65" in (ds.get("algos") or []) and dv.get("ok") and not dt.get("ok"),
           (ds.get("algos"), dv.get("ok"), dt.get("ok")))
    else:
        ck("C-beta20", "Master ML-DSA dual signing skipped (not available in this environment)", True, "skipped")

    c9 = agi_bridge.Bridge(root)
    t9 = c9.init_token(("read", "write"))["token"]
    srv9 = agi_bridge.ThreadingHTTPServer(("127.0.0.1", 0), agi_bridge.make_handler(c9))
    threading.Thread(target=srv9.serve_forever, daemon=True).start()
    base9 = "http://127.0.0.1:%d" % srv9.server_address[1]

    def call9(i, name, args):
        _, _, r = _http("POST", base9 + "/mcp", t9, {"jsonrpc": "2.0", "id": i, "method": "tools/call",
                                                     "params": {"name": name, "arguments": args}})
        return json.loads(((json.loads(r).get("result") or {}).get("content") or [{}])[0].get("text", "{}"))

    try:
        agi_policy.set_value(root, "remote_passport_issue_enabled", False)
        deny = call9(1, "passport_issue", {"member": remote_member})
        agi_policy.set_value(root, "remote_passport_issue_enabled", True)
        allow = call9(2, "passport_issue", {"member": remote_member, "note": "policy-enabled"})
    finally:
        srv9.shutdown()
    ck("C-beta21", "remote passport issuance is denied by default policy and allowed only after local enablement",
       (not deny.get("ok")) and "disabled by policy" in (deny.get("error") or "") and allow.get("ok"),
       (deny.get("error"), allow.get("error")))

    if include_stability:
        import agi_stability
        stab = agi_stability.run(root, runs=2)
        ck("C-beta22", "stability gate: 2 cold conformance runs PASS", stab.get("ok") and stab.get("runs") == 2,
           [r.get("failed") for r in stab.get("results", [])])
    else:
        ck("C-beta22", "stability gate skipped (nested stability run)", True, "skipped")

    passed = sum(1 for x in checks if x["ok"])
    return {"schema": SCHEMA, "sandbox": str(root), "checks": checks,
            "passed": passed, "total": len(checks),
            "verdict": "PASS" if passed == len(checks) else "ATTENTION"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Beta conformance matrix (C-beta1..C-beta22)")
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
